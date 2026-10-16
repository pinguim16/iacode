#!/usr/bin/env python3
"""Read bounded metadata from the newest owned quality run without retaining payloads."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))

from verify import verification_environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=ROOT)
    parser.add_argument("--commit")
    parser.add_argument("--published-verifier", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    if args.published_verifier:
        progress = json.loads((Path(__file__).resolve().parent.parent
                               / "FULL-VERIFY-PROGRESS.json").read_text())
        checkout = Path(progress["clone"]).resolve()
        if (checkout.name != "repository"
                or not checkout.parent.name.startswith("iacode-cp0010-full-verification-")):
            raise RuntimeError("the progress record does not name this checkpoint's verifier")
        args.commit = progress["subjectCommit"]
    if checkout != ROOT:
        observed = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=checkout, capture_output=True, text=True,
            check=True,
        ).stdout.strip()
        if not args.commit or observed != args.commit:
            raise RuntimeError("the inspected verifier checkout is not the explicit subject")
    os.environ.update(verification_environment(checkout))
    path = ROOT / "scripts/iacode/scenarios/quality_engine_e2e.py"
    spec = importlib.util.spec_from_file_location("owned_quality_output_probe", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("the live scenario observer is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    row = module.compose(
        "exec", "-T", "postgres", "sh", "-c",
        'PGPASSWORD="$POSTGRES_PASSWORD" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" '
        '-Atc "SELECT id FROM quality_runs ORDER BY created_at DESC LIMIT 1;"',
        merge_stderr=False,
    )
    identifier = row.stdout.strip()
    if not row.ok or not identifier:
        raise RuntimeError("no current owned quality run could be read")
    observed = module.compose(
        "exec", "-T", "api", "python", "-c", module.HISTORY_OUTPUT_OBSERVER,
        identifier, merge_stderr=False,
    )
    if not observed.ok:
        raise RuntimeError("the bounded history observer failed")
    detail = module.request("GET", f"/{identifier}")
    document = {"runId": identifier, "state": detail["run"]["state"],
                "subjectCommit": args.commit,
                "observedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "completedChecks": [{"checkId": item["checkId"], "status": item["status"]}
                                    for item in detail["results"]],
                "observation": json.loads(observed.stdout)}
    if args.report:
        target = (ROOT / args.report).resolve()
        if target.parent != Path(__file__).resolve().parent.parent:
            raise RuntimeError("diagnostic report must stay inside this checkpoint")
        if target.exists():
            raise RuntimeError("preserve the prior diagnostic observation")
        target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
