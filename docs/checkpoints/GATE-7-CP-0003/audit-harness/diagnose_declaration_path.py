"""Observe the actual cold-tag validator and its real archive validation delegates."""

from __future__ import annotations

import argparse
import builtins
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))


def child(identifier, import_mode):
    import ledger_common
    import validate_checkpoint

    observations, verifications, resolutions = [], [], []
    originals = []
    actual_import = builtins.__import__

    def observe_module(module):
        if any(item[0] is module for item in originals):
            return
        resolutions.append(
            {
                "module": module.__name__,
                "file": module.__file__,
                "searchPath": list(sys.path),
            }
        )
        for name, output in (("validate", observations), ("verify_declaration", verifications)):
            original = getattr(module, name)

            def observe(*arguments, _original=original, _output=output, **options):
                report = _original(*arguments, **options)
                _output.append(report)
                return report

            originals.append((module, name, original))
            setattr(module, name, observe)

    def observe_import(name, globals=None, locals=None, fromlist=(), level=0):
        module = actual_import(name, globals, locals, fromlist, level)
        if name == "review_bundle":
            observe_module(module)
        return module

    if import_mode == "preloaded":
        observe_module(actual_import("review_bundle"))

    def git(clone, *arguments):
        code, output = ledger_common.run_git(clone, "-c", "core.longpaths=true", *arguments)
        if code:
            raise RuntimeError(f"diagnostic Git query failed: {code}: {output}")
        return output

    # Match RecordedInputTests: actual public transport, own canonical tag, current external
    # validator, inherited current working directory. No historical source is edited.
    facts = {
        "kind": "ACTUAL_COLD_TAG_VALIDATOR_DIAGNOSTIC_NOT_ACCEPTANCE",
        "checkpoint": identifier,
        "importMode": import_mode,
        "consumerSource": "scripts/development-ledger/validate_checkpoint.py",
        "archiveConsumerSource": "scripts/development-ledger/review_bundle.py",
        "canonicalExitCode": None,
        "archiveValidationReports": observations,
        "declarationVerificationReports": verifications,
        "actualArchiveConsumerResolutions": resolutions,
        "preloadedControlIsNotFaithfulFailureReproduction": import_mode == "preloaded",
        "gateVerdictGranted": False,
    }
    owner_path = None
    try:
        with tempfile.TemporaryDirectory(prefix="iacode-sealed-") as temporary:
            owner_path = Path(temporary)
            clone = owner_path / "clone"
            if not ledger_common.published_clone(ROOT, clone):
                raise RuntimeError("ACTUAL_PUBLIC_CLONE_UNAVAILABLE_NO_HISTORICAL_VERDICT")
            checked = git(
                clone, "checkout", "--quiet", "--detach", "iacode-checkpoints/" + identifier
            )
            facts["checkoutOutput"] = checked
            facts["cloneHead"] = git(clone, "rev-parse", "HEAD")
            facts["cloneWasClean"] = not bool(git(clone, "status", "--porcelain"))
            facts["clonePath"] = str(clone)
            with (
                mock.patch.object(builtins, "__import__", new=observe_import),
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        str(ROOT / "scripts/development-ledger/validate_checkpoint.py"),
                        "--root",
                        str(clone),
                    ],
                ),
            ):
                facts["canonicalExitCode"] = validate_checkpoint.main()
            facts["cloneStayedClean"] = not bool(git(clone, "status", "--porcelain"))
    finally:
        for module, name, original in reversed(originals):
            setattr(module, name, original)
        facts["temporaryCloneRemoved"] = owner_path is not None and not owner_path.exists()
        print("DECLARATION_DIAGNOSTIC=" + json.dumps(facts), flush=True)
    return 0


def main():
    from audit_runner_bridge import Job, run_owned
    from ledger_common import find_secrets, scope_fingerprint, utc_now, write_json
    from native_process import WindowsJob

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoint",
        required=True,
        choices=("GATE-5-CP-0001", "GATE-6-CP-0001", "GATE-7-CP-0001"),
    )
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--import-mode", choices=("preloaded", "native"), default="preloaded")
    options = parser.parse_args()
    if options.child:
        return child(options.checkpoint, options.import_mode)
    directory = CHECKPOINT / "declaration-diagnostics"
    directory.mkdir(exist_ok=True)
    output = directory / f"run-{len(list(directory.glob('run-*'))) + 1:04d}"
    output.mkdir()
    source = scope_fingerprint(ROOT)
    receipt = {
        "kind": "CANONICAL_VALIDATOR_DIAGNOSTIC_NOT_ACCEPTANCE",
        "checkpoint": options.checkpoint,
        "importMode": options.import_mode,
        "startedAt": utc_now(),
        "sourceFingerprint": source,
        "acceptanceGranted": False,
    }
    with tempfile.TemporaryDirectory(prefix="iacode-m2cp3-public-quality-") as temporary:
        owner = Path(temporary).resolve()
        if owner.parent != Path(tempfile.gettempdir()).resolve() or owner.is_junction():
            raise ValueError("unexpected freshly created diagnostic owner")
        child_temporary = owner / "temporary"
        child_temporary.mkdir()
        environment = {**os.environ, "TMP": str(child_temporary), "TEMP": str(child_temporary)}
        arguments = (
            sys.executable,
            str(Path(__file__).resolve()),
            "--checkpoint",
            options.checkpoint,
            "--import-mode",
            options.import_mode,
            "--child",
        )
        execution, streams = run_owned(
            Job(arguments, 1800), ROOT, environment, find_secrets, WindowsJob
        )
        receipt["execution"] = execution
        for name, raw in streams.items():
            with (output / name).open("xb") as stream:
                stream.write(raw)
        write_json(output / "RECEIPT.json", receipt)
    receipt.update(
        finishedAt=utc_now(),
        temporaryOwnerRemoved=not owner.exists(),
        sourceUnchanged=scope_fingerprint(ROOT) == source,
    )
    write_json(output / "RECEIPT.json", receipt)
    primary = execution["producer"]
    completed = (
        primary["status"] == "COMPLETED"
        and primary["exitCode"] == 0
        and execution["cleanup"]["result"] == "PASS"
        and not any(primary[name]["refusal"] for name in ("stdout", "stderr"))
        and receipt["temporaryOwnerRemoved"]
        and receipt["sourceUnchanged"]
    )
    print(
        json.dumps(
            {
                "diagnosticCompleted": completed,
                "receipt": (output / "RECEIPT.json").relative_to(CHECKPOINT).as_posix(),
            }
        )
    )
    return 0 if completed else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
