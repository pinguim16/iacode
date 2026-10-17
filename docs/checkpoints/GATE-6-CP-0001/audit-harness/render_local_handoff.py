"""Repair only continuation artifacts using the canonical checked renderer; no verdict change."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, use_utf8_stdout


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS":
        raise ValueError("only unsealed implementing continuation may be rendered")
    spec = importlib.util.spec_from_file_location("gate6_source_renderer", Path(__file__).with_name("assemble_source_ready.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (CHECKPOINT / "HANDOFF.md").write_text(module.render_handoff(module.local_handoff_sections()), encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(module.render_next(state["nextAllowedAction"]), encoding="utf-8", newline="\n")
    print("CONTINUATION_RENDERED canonicalHeadings=complete; no finding or Gate promoted")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
