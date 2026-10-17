"""Register actual structural prevention after renderer and canonical checkpoint acceptance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("only the current unsealed implementing checkpoint may change")
    records = {row["id"]: row for row in (json.loads(line) for line in
        (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    for identifier in ("cmd-0085", "cmd-0086", "cmd-0091", "cmd-0092"):
        if records[identifier]["exitCode"] != 0:
            raise ValueError("actual renderer and canonical checkpoint acceptance required")
    names = ["test_local_handoff_renderer_preserves_the_complete_canonical_contract",
             "test_local_handoff_renderer_refuses_omitted_or_empty_sections_and_next_action"]
    registry = load_json(ROOT / ".iacode/memory/guardrails/registry.json")
    if any(row["guardrailId"] == "GRD-0142" for row in registry["guardrails"]):
        raise ValueError("new guard identity must not replace an existing guard")
    registry["guardrails"].append({"guardrailId": "GRD-0142",
        "title": "Continuation renderers preserve every canonical structural section",
        "kind": "test", "reference": names[0], "verifiedBy": names, "lessons": ["LSN-0140"],
        "removingItWouldAllow": "A readable summary to replace mandatory structured handoff/next-action content without an executable authoring guard."})
    write_json(ROOT / ".iacode/memory/guardrails/registry.json", registry)
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0140")
    lesson["status"] = "GUARDED"
    lesson["guardrails"] = ["GRD-0142"]
    lesson["prevention"] = [{"kind": "test", "reference": name,
        "description": "Actual canonical renderer output and every omitted/empty-section refusal."} for name in names]
    lesson["updatedAt"] = utc_now()
    lesson["notes"] = "Cmd-0081's actual finalizer refusal remains. Corrected renderer cmd-0085, all22 root controls including positive/adverse structure cmd-0086 and actual serialized CHECKPOINT_VALID cmd-0091/0092 pass without changing the canonical validator. Full immutable assurance and independent M2 remain separate."
    save_lessons(ROOT, lessons)
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    finding = next(row for row in findings["findings"] if row["findingId"] == "G6-INT-009")
    finding["status"] = "CLOSED"
    finding["resolutionEvidence"] = ["command:cmd-0085", "command:cmd-0086", "command:cmd-0091", "command:cmd-0092"]
    finding["resolution"] = "Canonical headings are consumed from their owning validator and every section requires substantive content. Actual output, omission/empty mutations and current checkpoint acceptance pass; no required heading or check was removed."
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    print("G6-INT-009 CLOSED; LSN-0140/GRD-0142 causally guarded; whole-Gate verdict not issued")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
