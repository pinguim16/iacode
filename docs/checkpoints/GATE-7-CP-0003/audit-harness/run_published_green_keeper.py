"""Whole canonical Green Keeper in exact public transport; never filter local private refs."""

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from audit_runner_bridge import Job, run_owned
from ledger_common import find_secrets, scope_fingerprint, utc_now, write_json
from native_process import WindowsJob
from owned_docker_scope import child_environment
from run_full_verification import REMOTE, command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    if (re.fullmatch(r"[0-9a-f]{40}", args.commit) is None
            or re.fullmatch(r"iacode-subjects/GATE-7-CP-0003-runtime-v[1-9][0-9]*", args.tag) is None):
        raise ValueError("Exact immutable current public progress subject required")
    folder = CHECKPOINT / "published-green-keeper"
    folder.mkdir(exist_ok=True)
    index = len(list(folder.glob("run-*"))) + 1
    output = folder / f"run-{index:04d}"
    output.mkdir()
    fingerprint = scope_fingerprint(ROOT)
    commands_path = CHECKPOINT / "COMMANDS.jsonl"
    rework_path = CHECKPOINT / "REWORK-LOG.jsonl"
    original_commands = commands_path.read_bytes()
    original_rework = rework_path.read_bytes() if rework_path.exists() else b""
    receipt = {"observedAt": utc_now(), "kind": "COMPLETE_CANONICAL_GREEN_KEEPER_PUBLIC_TRANSPORT",
               "subjectCommit": args.commit, "subjectTag": args.tag, "sourceFingerprint": fingerprint,
               "result": "FAIL", "allMandatoryGatesRequested": True, "gateSelectionOverride": False,
               "localPrivateRefsFilteredOrChanged": False, "sourceEdited": False,
               "cloneCredentialHelperDisabled": True, "cloneInteractivePromptsDisabled": True,
               "canonicalEvidenceImported": False}
    with tempfile.TemporaryDirectory(prefix="iacode-m2cp3-public-quality-") as temporary:
        owner = Path(temporary).resolve()
        if owner.parent != Path(tempfile.gettempdir()).resolve() or owner.is_symlink() or owner.is_junction():
            raise ValueError("Unexpected fresh public quality owner")
        clone = owner / "repository"
        command(["git", "-c", "core.longpaths=true", "clone", "--no-local", REMOTE, str(clone)], owner)
        if (command(["git", "rev-parse", "HEAD"], clone) != args.commit
                or command(["git", "rev-parse", args.tag + "^{commit}"], clone) != args.commit
                or command(["git", "rev-parse", "origin/main"], clone) != args.commit
                or command(["git", "status", "--porcelain"], clone)
                or scope_fingerprint(clone) != fingerprint):
            raise ValueError("Exact public clean subject/current source mismatch")
        private_checkpoint = clone / CHECKPOINT.relative_to(ROOT)
        if ((private_checkpoint / "COMMANDS.jsonl").read_bytes() != original_commands
                or (private_checkpoint / "REWORK-LOG.jsonl").read_bytes() != original_rework):
            raise ValueError("Serialize publication and command evidence before public quality")
        # Mandatory quality gates are decision/engine suites, never live provider acceptance.
        shutil.copyfile(clone / "infra/compose/.env.example", clone / "infra/compose/.env")
        environment = child_environment()
        from ledger_common import load_json
        environment["COMPOSE_PROJECT_NAME"] = load_json(CHECKPOINT / "OWNED-DOCKER-SCOPE.json")["inheritedOwnedProject"]
        environment["IACODE_VERSION"] = "0.1.0"
        arguments = [sys.executable, "scripts/development-ledger/green_keeper.py", "--trigger",
                     "Current complete corrective assurance from an exact public transported subject",
                     "--root-cause", "M2 literal invocation/cleanup evidence and measured adapter/UTF-8 guard corrections"]
        execution, streams = run_owned(Job(tuple(arguments), 43200), clone, environment, find_secrets, WindowsJob)
        receipt["execution"] = execution
        for name, raw in streams.items():
            with (output / name).open("xb") as stream:
                stream.write(raw)
        # Preserve canonical outputs byte-for-byte before interpreting or removing the owner.
        generated = {}
        for name in ("COMMANDS.jsonl", "REWORK-LOG.jsonl"):
            path = private_checkpoint / name
            raw = path.read_bytes()
            if find_secrets(raw.decode("utf-8", errors="strict")):
                raise ValueError("Unsafe canonical quality observation")
            with (output / name).open("xb") as stream:
                stream.write(raw)
            generated[name] = raw
        receipt["cloneSourceUnchanged"] = scope_fingerprint(clone) == fingerprint
        receipt["workingSourceUnchanged"] = scope_fingerprint(ROOT) == fingerprint
        write_json(output / "RECEIPT.json", receipt)
        if (commands_path.read_bytes() != original_commands
                or rework_path.read_bytes() != original_rework
                or not generated["COMMANDS.jsonl"].startswith(original_commands)
                or not generated["REWORK-LOG.jsonl"].startswith(original_rework)):
            raise ValueError("Do not overwrite concurrent working ledger evidence")
        # Only original append-only canonical bytes are imported. No argv/cwd/exit is rewritten.
        with commands_path.open("ab") as stream:
            stream.write(generated["COMMANDS.jsonl"][len(original_commands):])
        with rework_path.open("ab") as stream:
            stream.write(generated["REWORK-LOG.jsonl"][len(original_rework):])
        receipt["canonicalEvidenceImported"] = True
        receipt["importedCommandsSha256"] = hashlib.sha256(generated["COMMANDS.jsonl"]).hexdigest()
        rows = [json.loads(row) for row in generated["REWORK-LOG.jsonl"].splitlines() if row.strip()]
        success = (execution["producer"]["status"] == "COMPLETED" and execution["producer"]["exitCode"] == 0
                   and execution["cleanup"]["result"] == "PASS"
                   and not any(execution["producer"][key]["refusal"] for key in ("stdout", "stderr"))
                   and receipt["cloneSourceUnchanged"] and receipt["workingSourceUnchanged"]
                   and rows[-1]["result"] == "GREEN")
        receipt["result"] = "PASS" if success else "FAIL"
        receipt["temporaryClone"] = str(clone)
    receipt["temporaryCloneRemoved"] = not owner.exists()
    if not receipt["temporaryCloneRemoved"]:
        receipt["result"] = "FAIL"
    receipt["finishedAt"] = utc_now()
    write_json(output / "RECEIPT.json", receipt)
    print(json.dumps({"result": receipt["result"], "canonicalEvidenceImported": receipt["canonicalEvidenceImported"],
                      "temporaryCloneRemoved": receipt["temporaryCloneRemoved"],
                      "independentVerdictGranted": False}))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
