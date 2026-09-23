#!/usr/bin/env python3
"""M1-F-003, behaviourally: the old validator accepts a local object the new one refuses.

The unit tests of the correction fail on the old code partly because a helper does not exist
there. This measures the behaviour itself, with the old validator run unchanged from a worktree of
the commit before the correction:

1. a transport clone of this repository holds every preserved commit, reached by its tag;
2. each preserved tag is deleted in that clone, so its commit stays in the clone's object store
   and no published reference reaches it — `LOCAL OBJECT EXISTS`, `PUBLISHED OBJECT` does not;
3. the sealed checkpoint that names the commit is checked out at its own tag and judged by the old
   validator and by the corrected one.

The old validator accepts (the blind spot: only the object was asked about), the corrected one
refuses and says the object exists only locally. With the tags restored both accept — the null
control, which shows the refusal belongs to the missing reference and to nothing else.

    python validator_blind_spot.py --base 0e60b96 --report ../VALIDATOR-BLIND-SPOT.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import published_clone, utc_now  # noqa: E402


def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                               timeout=1800)
    return completed.returncode, completed.stdout.strip()


def first(output: str) -> str:
    return " ".join(output.splitlines()[:2])[:400]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    scratch = Path(tempfile.mkdtemp(prefix="iacode-blind-spot-"))
    old = scratch / "old-tooling"
    clone = scratch / "published"
    cases = []
    try:
        code, output = run(["git", "worktree", "add", "--detach", "--quiet", str(old),
                            arguments.base], ROOT)
        if code != 0:
            raise SystemExit(output)
        if not published_clone(ROOT, clone):
            raise SystemExit("the transport clone failed")
        listed = run(["git", "for-each-ref", "--format=%(refname) %(objectname)",
                      "refs/tags/iacode-preserved"], clone)[1]
        preserved = dict(line.split() for line in listed.splitlines() if line.strip())
        # Only sealed checkpoints are subjects: the anchored ones. This checkpoint's own ledger
        # names the preserved commits too (the commands that tagged them), and the first run of
        # this harness picked it for that reason (cmd-0030).
        chain = json.loads((clone / ".iacode" / "anchors" / "checkpoint-chain.json")
                           .read_text(encoding="utf-8"))
        checkpoints = sorted(item["checkpointId"] for item in chain["anchors"])
        subjects = {}
        for reference, commit in preserved.items():
            subjects[reference] = next(
                name for name in checkpoints
                if commit in (clone / "docs" / "checkpoints" / name / "COMMANDS.jsonl")
                .read_text(encoding="utf-8"))
        validators = {"old": old / "scripts" / "development-ledger" / "validate_checkpoint.py",
                      "corrected": ROOT / "scripts" / "development-ledger" /
                      "validate_checkpoint.py"}
        for reference, commit in sorted(preserved.items()):
            subject = subjects[reference]
            case = {"reference": reference, "commit": commit, "checkpoint": subject}
            for label, present in (("withReference", True), ("withoutReference", False)):
                if not present:
                    run(["git", "update-ref", "-d", reference], clone)
                run(["git", "checkout", "--quiet", "--detach",
                     f"refs/tags/iacode-checkpoints/{subject}"], clone)
                exists = run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], clone)[0] == 0
                verdicts = {}
                for name, validator in validators.items():
                    code, output = run([sys.executable, str(validator), "--root", str(clone)],
                                       ROOT)
                    verdicts[name] = {"exitCode": code, "output": first(output)}
                case[label] = {"localObjectExists": exists, "validators": verdicts}
                run(["git", "checkout", "--quiet", "main"], clone)
            run(["git", "update-ref", reference, commit], clone)
            case["ok"] = (
                case["withReference"]["validators"]["old"]["exitCode"] == 0
                and case["withReference"]["validators"]["corrected"]["exitCode"] == 0
                and case["withoutReference"]["localObjectExists"]
                and case["withoutReference"]["validators"]["old"]["exitCode"] == 0
                and case["withoutReference"]["validators"]["corrected"]["exitCode"] != 0
                and "exists here only as a local object"
                in case["withoutReference"]["validators"]["corrected"]["output"])
            cases.append(case)
            print(f"[{'PASS' if case['ok'] else 'FAIL'}] {reference} -> {subject}: without the "
                  f"reference old={case['withoutReference']['validators']['old']['exitCode']} "
                  f"corrected={case['withoutReference']['validators']['corrected']['exitCode']}")
    finally:
        run(["git", "worktree", "remove", "--force", str(old)], ROOT)
        run(["git", "worktree", "prune"], ROOT)
        shutil.rmtree(scratch, ignore_errors=True)
    base = run(["git", "rev-parse", arguments.base], ROOT)[1]
    report = {
        "schemaVersion": "1.0.0", "artifact": "VALIDATOR-BLIND-SPOT", "finding": "M1-F-003",
        "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(), "oldToolingCommit": base,
        "cases": cases, "result": "PASS" if cases and all(item["ok"] for item in cases)
        else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"VALIDATOR_BLIND_SPOT={report['result']} cases={len(cases)}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
