"""Register the measured cold-consumer import failure before implementing a repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)

from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from lessons import load_lessons, recurrence_key, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def observation(number):
    directory = CHECKPOINT / f"declaration-diagnostics/run-{number:04d}"
    receipt = load_json(directory / "RECEIPT.json")
    execution = receipt["execution"]
    producer = execution["producer"]
    if (
        producer["status"] != "COMPLETED"
        or producer["exitCode"] != 0
        or execution["cleanup"]["result"] != "PASS"
        or receipt["sourceFingerprint"] != scope_fingerprint(ROOT)
        or not receipt["sourceUnchanged"]
        or not receipt["temporaryOwnerRemoved"]
    ):
        raise ValueError("Completed unchanged real diagnostic required")
    for name in ("stdout", "stderr"):
        raw = (directory / (name + ".log")).read_bytes()
        fact = producer[name]
        if (
            fact["refusal"]
            or len(raw) != fact["bytes"]
            or hashlib.sha256(raw).hexdigest() != fact["sha256"]
        ):
            raise ValueError("Original safe diagnostic bytes required")
    text = (directory / "stdout.log").read_text(encoding="utf-8")
    facts = [
        json.loads(line.removeprefix("DECLARATION_DIAGNOSTIC="))
        for line in text.splitlines()
        if line.startswith("DECLARATION_DIAGNOSTIC=")
    ]
    if len(facts) != 1:
        raise ValueError("One original canonical observation required")
    return facts[0]


def guard():
    from derive_requirements import render_closure, render_matrix
    from lesson_preflight import render_markdown
    from lessons import build_preflight

    destination = CHECKPOINT / "IMPORT-ISOLATION-LOCAL-PREVENTION.json"
    lessons = load_lessons(ROOT)
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0153")
    item = next(row for row in rework["items"] if row["id"] == "IMPORT-ISOLATION-001")
    if destination.exists() or lesson["status"] != "CONFIRMED" or item["status"] != "OPEN":
        raise ValueError("Exact open one-shot local prevention required")
    expected = ["GATE-5-CP-0001", "GATE-6-CP-0001", "GATE-7-CP-0001"]
    evidence = ["causal-attempts/discovery-isolation/run-0003.json"]
    for number, identifier in zip((3, 4, 5), expected, strict=True):
        facts = observation(number)
        reports = facts["declarationVerificationReports"]
        if (
            facts["checkpoint"] != identifier
            or facts["importMode"] != "native"
            or facts["canonicalExitCode"] != 0
            or not facts["cloneWasClean"]
            or not facts["cloneStayedClean"]
            or not facts["temporaryCloneRemoved"]
            or Path(facts["actualArchiveConsumerResolutions"][-1]["file"])
            != ROOT / "scripts/development-ledger/review_bundle.py"
            or len(reports) != 1
            or reports[0]["result"] != "PASS"
            or reports[0]["findings"]
            or reports[0]["reconstruction"]["producerExitCodes"] != [0, 0]
            or not reports[0]["reconstruction"]["byteIdentical"]
        ):
            raise ValueError("Actual unchanged unpreloaded complete historical validator required")
        evidence.extend(
            (
                f"declaration-diagnostics/run-{number:04d}/RECEIPT.json",
                f"declaration-diagnostics/run-{number:04d}/stdout.log",
            )
        )
    proof = load_json(CHECKPOINT / evidence[0])
    source = scope_fingerprint(ROOT)
    if (
        proof["exitCode"] != 0
        or proof["sourceFingerprint"] != source
        or not proof["sourceUnchanged"]
    ):
        raise ValueError("Actual current unchanged discovery controls required")
    for fact in proof["streams"].values():
        raw = (ROOT / fact["path"]).read_bytes()
        if (
            fact["refused"]
            or len(raw) != fact["bytes"]
            or hashlib.sha256(raw).hexdigest() != fact["sha256"]
        ):
            raise ValueError("Original safe current discovery output required")
    tests = [
        "M2DiscoveryIsolationTests." + name
        for name in (
            "test_actual_valid_null_counts_inherited_and_skipped_cases_without_running_them",
            "test_actual_inspected_import_cannot_replace_the_late_current_consumer",
            "test_same_named_preloaded_test_is_restored_but_never_counted_for_another_root",
            "test_repeated_real_roots_keep_their_own_exact_discovery_counts",
            "test_a_real_load_tests_error_is_refused_instead_of_counted_as_one_case",
            "test_an_actual_uncaught_import_failure_also_restores_caller_state",
            "test_the_shared_default_loader_is_not_mutated_by_counting",
            "test_missing_suite_remains_zero_without_changing_import_state",
        )
    ]
    if any(row["guardrailId"] == "GRD-0156" for row in registry["guardrails"]):
        raise ValueError("Never duplicate a guardrail identity")
    retrospective = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0003.md"
    text = retrospective.read_text(encoding="utf-8")
    old = (
        "LSN-0153 is CONFIRMED, not GUARDED: discovery must preserve "
        "the auditing consumer's import bindings.\nActual before/after"
        " controls, unchanged unpreloaded historical validators and f"
        "ull current assurance\nare separate requirements. No new guar"
        "drail or independent approval is claimed prematurely."
    )
    if text.count(old) != 1:
        raise ValueError("Exact unguarded retrospective transition required")
    text = text.replace(
        old,
        (
            "LSN-0153 has measured local prevention under GRD-0156: real "
            "discovery controls and all three\nunchanged unpreloaded histo"
            "rical validators pass, including original byte-identical dec"
            "larations.\nThis local guard does not grant whole immutable a"
            "ssurance or independent milestone approval."
        ),
        1,
    )
    now = utc_now()
    lesson.update(
        status="GUARDED",
        updatedAt=now,
        guardrails=["GRD-0156"],
        resolution=(
            "Actual unchanged discovery/null/adverse/refusal controls and"
            " complete unpreloaded current validation of original Gates5/"
            "6/7 tags pass. Scoped import-binding prevention is locally m"
            "easured; fresh whole source-epoch quality, functional and in"
            "dependent milestone assurance remain mandatory."
        ),
        prevention=[
            {
                "kind": "test",
                "reference": name,
                "description": (
                    "Executed real local discovery control; not an independent verdict."
                ),
            }
            for name in tests
        ],
    )
    lesson["evidence"] += [
        "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix() for name in evidence
    ]
    registry["guardrails"].append(
        {
            "guardrailId": "GRD-0156",
            "title": "Real discovery restores caller import bindings",
            "kind": "test",
            "reference": tests[1],
            "verifiedBy": tests,
            "lessons": ["LSN-0153"],
            "removingItWouldAllow": (
                "Inspected historical test imports to select old auditing hel"
                "pers or a cached foreign test module to change the measured "
                "denominator."
            ),
        }
    )
    item.update(
        status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING", currentProof=evidence
    )
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    row = next(row for row in closure["requirements"] if row["sourceRef"] == "lesson:LSN-0153")
    row.update(
        implementationStatus="PARTIAL",
        finalStatus="PARTIAL",
        justification=(
            "Measured local import-state prevention; whole current immutable assurance pending."
        ),
    )
    row["implementationEvidence"] += ["file:scripts/development-ledger/derive_counts.py"]
    row["testEvidence"] += ["file:tests/test_m2_discovery_isolation.py"]
    row["negativeTestEvidence"] += ["checkpoint:causal-attempts/discovery-isolation/run-0001.json"]
    row["validationEvidence"] += ["checkpoint:" + name for name in evidence]
    row["guardrailEvidence"] += ["test:" + name for name in tests]
    row["documentationEvidence"] += [
        ("file:docs/adr/ADR-0064-unittest-discovery-restores-caller-import-bindings.md")
    ]
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    matrix_row = next(
        value for value in matrix["requirements"] if value["sourceRef"] == row["sourceRef"]
    )
    matrix_row.update(status="PARTIAL", justification=row["justification"])
    for field in (
        "implementationEvidence",
        "testEvidence",
        "documentationEvidence",
        "validationEvidence",
    ):
        matrix_row[field] = list(row[field])
    save_lessons(ROOT, lessons)
    write_json(registry_path, registry)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    retrospective.write_text(text, encoding="utf-8", newline="\n")
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        render_closure(closure), encoding="utf-8", newline="\n"
    )
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(
        render_matrix(matrix), encoding="utf-8", newline="\n"
    )
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    write_json(
        destination,
        {
            "recordedAt": now,
            "result": "LOCAL_PREVENTION_NOT_WHOLE_ACCEPTANCE",
            "proofSourceFingerprint": source,
            "nextSourceFingerprint": scope_fingerprint(ROOT),
            "lesson": "LSN-0153",
            "guardrail": "GRD-0156",
            "evidence": evidence,
            "independent": False,
        },
    )
    print("LSN-0153 / GRD-0156 locally demonstrated; fresh whole current assurance remains due")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guard", action="store_true")
    options = parser.parse_args()
    if options.guard:
        return guard()
    null, failure = observation(1), observation(2)
    resolutions = failure["actualArchiveConsumerResolutions"]
    if (
        null["canonicalExitCode"] != 0
        or failure["canonicalExitCode"] != 1
        or failure["importMode"] != "native"
        or len(resolutions) != 1
        or not Path(resolutions[0]["file"]).is_relative_to(Path(failure["clonePath"]))
        or not failure["cloneWasClean"]
        or not failure["cloneStayedClean"]
        or not failure["temporaryCloneRemoved"]
        or failure["declarationVerificationReports"][0]["result"] != "FAIL"
    ):
        raise ValueError(
            "Actual unpreloaded foreign-consumer failure and preloaded control required"
        )
    lessons = load_lessons(ROOT)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    if any(row["lessonId"] == "LSN-0153" for row in lessons) or any(
        row["id"] == "IMPORT-ISOLATION-001" for row in rework["items"]
    ):
        raise ValueError("One-shot registration must not be replayed")
    now = utc_now()
    evidence = [
        "file:" + (CHECKPOINT / path).relative_to(ROOT).as_posix()
        for path in (
            "declaration-diagnostics/run-0001/RECEIPT.json",
            "declaration-diagnostics/run-0001/stdout.log",
            "declaration-diagnostics/run-0002/RECEIPT.json",
            "declaration-diagnostics/run-0002/stdout.log",
            "published-green-keeper/run-0004/RECEIPT.json",
            "IMPORT-ISOLATION-001.json",
        )
    ]
    lesson = {
        "lessonId": "LSN-0153",
        "title": "Test discovery must not replace the auditing consumer's import environment",
        "category": "tooling",
        "severity": "HIGH",
        "source": {
            "gate": "GATE-7",
            "checkpoint": CHECKPOINT.name,
            "finding": "IMPORT-ISOLATION-001",
        },
        "symptom": (
            "A current cold-tag validator loads the inspected historical "
            "review_bundle after test counting and loses the current chil"
            "d-scoped transport correction."
        ),
        "rootCauseSummary": (
            "In-process unittest discovery executes inspected test-module"
            " imports without restoring sys.path or module-cache bindings"
            ". Late current consumer imports then resolve inspected histo"
            "rical helpers."
        ),
        "resolution": (
            "Cause confirmed by native import-origin failure beside a pre"
            "loaded current-consumer control. Repair and real causal regr"
            "essions are pending; no prevention or whole acceptance is cl"
            "aimed."
        ),
        "prevention": [],
        "evidence": evidence,
        "applicability": {
            "gates": ["*"],
            "scopes": [],
            "technologies": [],
            "modules": [],
            "requiredCheck": (
                "Preserve exact real unittest discovery counts while restorin"
                "g caller import state on success and failure, including coll"
                "iding test modules and repeated inspected roots."
            ),
            "requiredEvidence": (
                "Real adverse and valid null discovery controls, unchanged co"
                "ld-tag canonical validation and complete current quality."
            ),
        },
        "status": "CONFIRMED",
        "recurrenceKey": recurrence_key(
            "tooling",
            ("unittest discovery leaks inspected import environment into auditing consumer"),
        ),
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": {
            "sourceType": "repository-generated",
            "provider": "local-execution",
            "model": None,
            "ownership": "project-generated engineering evidence",
            "license": "not-applicable",
            "notes": (
                "Actual published immutable tag and original diagnostic strea"
                "ms; no independent verdict."
            ),
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": "No explicit rights evidence.",
        },
        "guardrails": [],
    }
    rework["items"].append(
        {
            "id": "IMPORT-ISOLATION-001",
            "status": "OPEN",
            "classification": "NEW_CONFIRMED_FAILURE_CLASS LSN-0153",
            "evidence": "declaration-diagnostics/run-0002/RECEIPT.json",
            "commands": ["cmd-0472", "cmd-0473"],
            "observed": lesson["symptom"],
            "requiredCorrection": lesson["applicability"]["requiredCheck"],
            "distinction": (
                "LSN-0151 transport correction passes when current consumer i"
                "s selected; this separate import-state failure selects the u"
                "nchanged legacy implementation. No existing recurrence count"
                "er is reset or silently restored."
            ),
        }
    )
    write_json(
        CHECKPOINT / "IMPORT-ISOLATION-001.json",
        {
            "id": "IMPORT-ISOLATION-001",
            "recordedAt": now,
            "status": "CONFIRMED_OPEN",
            "beforeSourceFingerprint": scope_fingerprint(ROOT),
            "actualForeignConsumer": resolutions[0]["file"],
            "actualCanonicalExitCode": 1,
            "preloadedControlExitCode": 0,
            "originalDiagnostics": evidence[:4],
            "acceptanceGranted": False,
            "classification": rework["items"][-1]["classification"],
        },
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    save_lessons(ROOT, [*lessons, lesson])
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index([*lessons, lesson]), encoding="utf-8", newline="\n"
    )
    print("IMPORT-ISOLATION-001 registered; LSN-0153 CONFIRMED; no acceptance granted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
