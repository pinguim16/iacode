"""Apply the existing continuation contract to actual CP0003, preserving its preimage."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts/development-ledger"))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tests"))
from ledger_common import find_secrets, utc_now, write_json
from test_gate7_continuation import Gate7ContinuationContractTests
from validate_checkpoint import HANDOFF_HEADINGS

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    folder = CHECKPOINT / "continuation-attempts"
    folder.mkdir(exist_ok=True)
    output = folder / f"run-{len(list(folder.glob('run-*'))) + 1:04d}"
    output.mkdir()
    origin = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0003.md"
    raw = origin.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    if find_secrets(text):
        raise ValueError("Refuse unsafe original document")
    preimage = output / "RETROSPECTIVE.md.raw"
    with preimage.open("xb") as stream:
        stream.write(raw)
    guard = Gate7ContinuationContractTests()
    outcomes = []
    # Structural contract is evaluated before lesson membership. An empty lesson
    # fixture would not weaken the heading assertion, but use actual current source
    # lessons here rather than an artificial denominator.
    from lessons import load_lessons

    lessons = [row for row in load_lessons(ROOT) if row["source"]["checkpoint"] == CHECKPOINT.name]
    if not lessons:
        raise ValueError("Actual current checkpoint lessons required")
    checks = (
        (
            "handoff",
            lambda: guard.check_sections(
                (CHECKPOINT / "HANDOFF.md").read_text(encoding="utf-8"), HANDOFF_HEADINGS
            ),
        ),
        ("next", lambda: guard.check_next((CHECKPOINT / "NEXT.md").read_text(encoding="utf-8"))),
        ("retrospective", lambda: guard.check_retrospective(text, lessons)),
    )
    for name, check in checks:
        try:
            check()
        except AssertionError:
            outcomes.append({"document": name, "result": "FAIL"})
        else:
            outcomes.append({"document": name, "result": "PASS"})
    failed = any(row["result"] != "PASS" for row in outcomes)
    write_json(
        output / "RECEIPT.json",
        {
            "observedAt": utc_now(),
            "kind": "EXISTING_CONTRACT_ACTUAL_CP0003_DOCUMENTS",
            "result": "FAIL" if failed else "PASS",
            "checks": outcomes,
            "source": origin.relative_to(ROOT).as_posix(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "original": preimage.name,
            "lessons": [row["lessonId"] for row in lessons],
            "testImplementation": "tests/test_gate7_continuation.py",
            "independent": False,
        },
    )
    print(
        {
            "result": "FAIL" if failed else "PASS",
            "checks": outcomes,
            "receipt": (output / "RECEIPT.json").relative_to(CHECKPOINT).as_posix(),
        }
    )
    return int(failed)


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
