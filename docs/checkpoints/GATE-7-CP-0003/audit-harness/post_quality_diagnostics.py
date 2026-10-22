"""Retain actual post-cycle observations; never approve or modify a sealed subject."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/iacode"))
from audit_runner_bridge import Job, run_owned
from ledger_common import find_secrets, load_json, scope_fingerprint, utc_now, write_json
from lessons import load_lessons, register_recurrence, render_index, save_lessons
from native_process import WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def register_codepage():
    whole = load_json(CHECKPOINT / "published-green-keeper/run-0003/RECEIPT.json")
    causal = load_json(CHECKPOINT / "causal-attempts/inherited-streams/run-0002.json")
    if (
        whole["execution"]["producer"]["exitCode"] != 1
        or whole["execution"]["cleanup"]["result"] != "PASS"
        or whole["workingSourceUnchanged"] is not True
        or whole["temporaryCloneRemoved"] is not True
        or causal["exitCode"] != 1
        or causal["sourceUnchanged"] is not True
        or causal["sourceFingerprint"] != scope_fingerprint(ROOT)
        or any(row["refused"] for row in causal["streams"].values())
    ):
        raise ValueError("Actual unchanged complete and causal failures required")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    if any(row["id"] == "ROOT-CODEPAGE-001" for row in rework["items"]):
        raise ValueError("Never duplicate a registered recurrence")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0035")
    if lesson["status"] != "GUARDED":
        raise ValueError("Expected the previously restored guarded lesson")
    revised = register_recurrence(
        lesson,
        CHECKPOINT.name,
        "ROOT-CODEPAGE-001: the actual complete public cycle and unchanged whole-tree "
        "SubprocessDecodingTests reject a newly authored publication-test Git capture "
        "with text=True and no explicit encoding. Preserve the original guard and "
        "execute it again before the next publication.",
    )
    revised["resolution"] = (
        "The new ROOT-CODEPAGE-001 recurrence is open; earlier local restoration and "
        "all original failures remain historical, not current acceptance."
    )
    for name in (
        "published-green-keeper/run-0003/RECEIPT.json",
        "published-green-keeper/run-0003/stdout.log",
        "causal-attempts/inherited-streams/run-0002.json",
    ):
        reference = "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix()
        if reference not in revised["evidence"]:
            revised["evidence"].append(reference)
    lessons[lessons.index(lesson)] = revised
    rework["items"].append(
        {
            "id": "ROOT-CODEPAGE-001",
            "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE LSN-0035",
            "observed": "The unchanged codepage guard rejects the actual publication-test "
            "Git capture. No actual Unicode decoding crash is claimed.",
            "evidence": "causal-attempts/inherited-streams/run-0002.json",
            "originalWholeCycle": "published-green-keeper/run-0003/RECEIPT.json",
            "requiredCorrection": "State the decoder explicitly, exercise Unicode through "
            "the real capture, and execute the unchanged whole-tree guard before publication "
            "and the next complete mandatory cycle. No test weakening or old seal rewrite.",
        }
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    print("ROOT-CODEPAGE-001 REGISTERED; LSN-0035 CONFIRMED; acceptance not granted")
    return 0


def register_history():
    path = CHECKPOINT / "history-diagnostics/run-0001/RECEIPT.json"
    receipt = load_json(path)
    raw = path.with_name("stdout.log").read_bytes()
    execution = receipt["execution"]
    if (
        execution["producer"]["exitCode"] != 0
        or execution["cleanup"]["result"] != "PASS"
        or receipt["sourceUnchanged"] is not True
        or receipt["temporaryOwnerRemoved"] is not True
        or hashlib.sha256(raw).hexdigest() != execution["producer"]["stdout"]["sha256"]
        or execution["producer"]["stdout"]["refusal"] is not None
    ):
        raise ValueError("Completed unchanged safe actual diagnostic required")
    observed = json.loads(raw)
    clone = observed["subprocessResults"][0]
    if (
        clone["exitCode"] != 128
        or "Filename too long" not in clone["decodedCombinedOutput"]
        or observed["reconstruction"]["result"] != "FAIL"
    ):
        raise ValueError("Actual transport failure class not demonstrated")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    if any(row["id"] == "HISTORY-TRANSPORT-001" for row in rework["items"]):
        raise ValueError("Never duplicate a registered recurrence")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0151")
    if lesson["status"] != "GUARDED":
        raise ValueError("Expected the previously guarded Git-path lesson")
    revised = register_recurrence(
        lesson,
        CHECKPOINT.name,
        "HISTORY-TRANSPORT-001: the real unchanged reconstruction caller clones without "
        "a child-scoped long-path override. At the public runner's child-only temporary "
        "depth, clone exits128 with Filename too long before detached subject checkout. "
        "The existing guard covered object reads but not transport materialization.",
    )
    revised["resolution"] = (
        "Current transport recurrence remains open; no historical seal or declaration "
        "has been rewritten and no reconstruction failure is accepted."
    )
    for reference in (
        "file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0001/RECEIPT.json",
        "file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0001/stdout.log",
        "file:docs/checkpoints/GATE-7-CP-0003/published-green-keeper/run-0003/RECEIPT.json",
    ):
        if reference not in revised["evidence"]:
            revised["evidence"].append(reference)
    lessons[lessons.index(lesson)] = revised
    rework["items"].append(
        {
            "id": "HISTORY-TRANSPORT-001",
            "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE LSN-0151",
            "observed": "Actual clone exits128 on long checkpoint-observation filenames "
            "at the public runner's child temporary depth. The complete cycle reports "
            "three historical declaration failures; only CP0001 has a detailed diagnostic yet.",
            "evidence": "history-diagnostics/run-0001/RECEIPT.json",
            "requiredCorrection": "Extend child-only Git path handling to transport "
            "materialization, prove real deep/null/genuine-refusal controls and actual "
            "historical declarations without changing sealed bytes or global settings.",
        }
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    print("HISTORY-TRANSPORT-001 REGISTERED; LSN-0151 CONFIRMED; acceptance not granted")
    return 0


def diagnose_child(identifier, destination):
    import review_bundle

    checkpoint = ROOT / "docs/checkpoints" / identifier
    declaration = load_json(checkpoint / "REVIEW-BUNDLE-VALIDATION.json")
    actual_run = review_bundle.subprocess.run
    observations = []

    def observe_run(arguments, **options):
        result = actual_run(arguments, **options)
        if arguments[0] == "git" and any(value in arguments for value in ("clone", "checkout")):
            observations.append(
                {
                    "arguments": arguments,
                    "workingDirectory": str(options.get("cwd")),
                    "exitCode": result.returncode,
                    "decodedCombinedOutput": result.stdout,
                }
            )
        return result

    with mock.patch.object(review_bundle.subprocess, "run", side_effect=observe_run):
        reconstruction = review_bundle.reconstruct_twice_from_transport(
            ROOT, checkpoint, declaration["subject"]["commit"], destination
        )
    print(
        json.dumps(
            {
                "kind": "ACTUAL_CANONICAL_CALLER_DIAGNOSTIC_NOT_RAW_GIT_STREAMS_OR_ACCEPTANCE",
                "checkpoint": identifier,
                "temporaryBase": tempfile.gettempdir(),
                "subprocessResults": observations,
                "reconstruction": reconstruction,
                "declarationComparison": review_bundle.verify_declaration(
                    ROOT, checkpoint, declaration, reconstruction
                ),
            }
        )
    )
    return 0


def diagnose_history(identifier):
    folder = CHECKPOINT / "history-diagnostics"
    folder.mkdir(exist_ok=True)
    output = folder / f"run-{len(list(folder.glob('run-*'))) + 1:04d}"
    output.mkdir()
    fingerprint = scope_fingerprint(ROOT)
    receipt = {
        "startedAt": utc_now(),
        "kind": "HISTORICAL_RECONSTRUCTION_DIAGNOSTIC_NOT_ACCEPTANCE",
        "checkpoint": identifier,
        "sourceFingerprint": fingerprint,
    }
    # Reproduce the failed cycle's child-only temporary depth, never a global setting.
    with tempfile.TemporaryDirectory(prefix="iacode-m2cp3-public-quality-") as raw:
        owner = Path(raw).resolve()
        if owner.parent != Path(tempfile.gettempdir()).resolve():
            raise ValueError("Unexpected fresh diagnostic owner")
        temporary = owner / "temporary"
        temporary.mkdir()
        environment = {**os.environ, "TMP": str(temporary), "TEMP": str(temporary)}
        arguments = (
            sys.executable,
            str(Path(__file__).resolve()),
            "history-child",
            "--checkpoint",
            identifier,
            "--destination",
            str(owner / "diagnostic.zip"),
        )
        execution, streams = run_owned(
            Job(arguments, 1800), ROOT, environment, find_secrets, WindowsJob
        )
        receipt["execution"] = execution
        for name, content in streams.items():
            with (output / name).open("xb") as stream:
                stream.write(content)
        receipt["safeStreamHashes"] = {
            name: hashlib.sha256(content).hexdigest() for name, content in streams.items()
        }
        write_json(output / "RECEIPT.json", receipt)
    receipt.update(
        finishedAt=utc_now(),
        temporaryOwnerRemoved=not owner.exists(),
        sourceUnchanged=scope_fingerprint(ROOT) == fingerprint,
    )
    write_json(output / "RECEIPT.json", receipt)
    producer = execution["producer"]
    completed = (
        producer["status"] == "COMPLETED"
        and producer["exitCode"] == 0
        and execution["cleanup"]["result"] == "PASS"
        and not any(producer[name]["refusal"] for name in ("stdout", "stderr"))
        and receipt["temporaryOwnerRemoved"]
        and receipt["sourceUnchanged"]
    )
    print(json.dumps({"diagnosticCompleted": completed, "receipt": str(output / "RECEIPT.json")}))
    return 0 if completed else 1


def inherited_controls(kind):
    module, selector, folder = {
        "inherited-git": ("test_gate7_git_transport.py", None, "inherited-git"),
        "review-controls": (
            "test_gate4_quality_engine.py",
            "ReviewBundleTests",
            "review-reconstruction",
        ),
    }[kind]
    arguments = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", module, "-v"]
    if selector:
        arguments.extend(("-k", selector))
    directory = CHECKPOINT / "causal-attempts" / folder
    directory.mkdir(parents=True, exist_ok=True)
    prefix = directory / f"run-{len(list(directory.glob('run-*.json'))) + 1:04d}"
    fingerprint, started, clock = scope_fingerprint(ROOT), utc_now(), time.monotonic()
    execution, streams = run_owned(
        Job(tuple(arguments), 1800), ROOT, dict(os.environ), find_secrets, WindowsJob
    )
    producer = execution["producer"]
    receipt = {
        "startedAt": started,
        "finishedAt": utc_now(),
        "execution": execution,
        "sourceFingerprint": fingerprint,
        "sourceUnchanged": scope_fingerprint(ROOT) == fingerprint,
        "arguments": arguments,
        "exitCode": producer["exitCode"],
        "durationMs": int((time.monotonic() - clock) * 1000),
        "streams": {},
    }
    for name in ("stdout", "stderr"):
        fact = producer[name]
        raw = streams.get(name + ".log")
        path = prefix.with_suffix("." + name + ".log")
        if raw is not None:
            with path.open("xb") as stream:
                stream.write(raw)
        receipt["streams"][name] = {
            "bytes": fact["bytes"],
            "sha256": fact["sha256"],
            "refused": fact["refusal"] is not None,
            "path": path.relative_to(ROOT).as_posix() if raw is not None else None,
        }
    write_json(prefix.with_suffix(".json"), receipt)
    passed = (
        producer["status"] == "COMPLETED"
        and producer["exitCode"] == 0
        and execution["cleanup"]["result"] == "PASS"
        and receipt["sourceUnchanged"]
        and not any(row["refused"] for row in receipt["streams"].values())
    )
    print(
        json.dumps(
            {"result": "PASS" if passed else "FAIL", "receipt": str(prefix.with_suffix(".json"))}
        )
    )
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=(
            "register-codepage",
            "register-history",
            "history",
            "history-child",
            "inherited-git",
            "review-controls",
        ),
    )
    parser.add_argument(
        "--checkpoint", choices=("GATE-5-CP-0001", "GATE-6-CP-0001", "GATE-7-CP-0001")
    )
    parser.add_argument("--destination", type=Path)
    options = parser.parse_args()
    if options.action == "register-codepage":
        return register_codepage()
    if options.action == "register-history":
        return register_history()
    if options.action in {"inherited-git", "review-controls"}:
        return inherited_controls(options.action)
    if options.checkpoint is None:
        raise ValueError("Explicit historical subject required")
    if options.action == "history-child":
        if options.destination is None:
            raise ValueError("Exact disposable destination required")
        return diagnose_child(options.checkpoint, options.destination)
    return diagnose_history(options.checkpoint)


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
