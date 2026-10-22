"""Carry actual new evidence into the draft without granting whole-run acceptance."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from derive_requirements import render_closure, render_matrix
from ledger_common import load_json, scope_fingerprint, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    references = {"finding:M2-F-002", "lesson:LSN-0135"}
    for row in closure["requirements"]:
        if row["sourceRef"] in references:
            row.update(
                implementationStatus="PARTIAL",
                finalStatus="PARTIAL",
                justification=(
                    "Docker-path causal repair is observed; the same native evide"
                    "nce-loss class is reproduced and not yet repaired."
                ),
            )
            row["notes"] = (
                "Actual controlled callback fault after a real owned drain, n"
                "ot a real OS cleanup failure; no editor or Docker operation "
                "in the probe."
            )
            for name in (
                "causal-attempts/native-cleanup-evidence/run-0001.json",
                "causal-attempts/native-observation/run-0001.json",
            ):
                ref = "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix()
                if ref not in row["negativeTestEvidence"]:
                    row["negativeTestEvidence"].append(ref)
    for row in matrix["requirements"]:
        if row["sourceRef"] in references:
            row.update(
                status="PARTIAL",
                justification=(
                    "Native M2-F-002 extension remains open; all current integral"
                    " assurance is still required."
                ),
            )
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        render_closure(closure), encoding="utf-8", newline="\n"
    )
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(
        render_matrix(matrix), encoding="utf-8", newline="\n"
    )
    state = load_json(CHECKPOINT / "STATE.json")
    state["updatedAt"] = utc_now()
    state["nextAllowedAction"] = (
        "Observe the actual stable root baseline exit and preserve it"
        "s streams. Then register the bridge path lesson, repair phys"
        "ical confinement and the native M2-F-002 extension, and reru"
        "n complete current assurance. Clean only proven owned waste "
        "after producers finish. Seal before any new independent audi"
        "tor; no Gate8."
    )
    state["requirementsMatrix"]["partial"] = sum(
        row["status"] == "PARTIAL" for row in matrix["requirements"]
    )
    state["greenKeeper"]["unresolvedReworkItems"] = 3
    write_json(CHECKPOINT / "STATE.json", state)
    active = load_json(CHECKPOINT / "ACTIVE-VALIDATION.json")
    active.update(recordedAt=utc_now(), sourceFingerprint=scope_fingerprint(ROOT))
    write_json(CHECKPOINT / "ACTIVE-VALIDATION.json", active)
    print("Draft evidence updated; no closed finding, seal, whole-run success or audit verdict")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
