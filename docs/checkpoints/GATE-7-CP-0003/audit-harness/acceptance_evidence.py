"""Read completed current evidence; never execute tests or manufacture a passing verdict."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
BASELINE = "GATE-7-CP-0001"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))


def original_streams(directory, execution):
    from audit_runner_bridge import regular
    from ledger_common import LedgerError, find_secrets

    producer = execution["producer"]
    if (
        producer.get("status") != "COMPLETED"
        or producer.get("exitCode") != 0
        or execution.get("cleanup", {}).get("result") != "PASS"
    ):
        raise LedgerError("actual completed producer and native cleanup must pass")
    for name in ("stdout", "stderr"):
        path = directory / (name + ".log")
        regular(path, CHECKPOINT)
        raw, fact = path.read_bytes(), producer[name]
        if (
            fact.get("refusal") is not None
            or type(fact.get("bytes")) is not int
            or len(raw) != fact["bytes"]
            or hashlib.sha256(raw).hexdigest() != fact.get("sha256")
            or find_secrets(raw.decode("utf-8", errors="strict"))
        ):
            raise LedgerError("actual original stream identity or privacy does not resolve")


def current_publication():
    from ledger_common import LedgerError, load_json

    candidates = []
    for path in CHECKPOINT.glob("RUNTIME-V*-PUBLICATION.json"):
        match = re.fullmatch(r"RUNTIME-V([1-9][0-9]*)-PUBLICATION\.json", path.name)
        if match:
            candidates.append((int(match[1]), path))
    if not candidates:
        raise LedgerError("an actual immutable progress publication is required")
    version, path = max(candidates)
    publication = load_json(path)
    expected = f"iacode-subjects/{CHECKPOINT.name}-runtime-v{version}"
    if (
        publication.get("kind") != "POST_PUBLICATION_OBSERVATION_NOT_CANONICAL_SEAL"
        or publication.get("tag") != expected
        or re.fullmatch(r"[0-9a-f]{40}", str(publication.get("commit"))) is None
    ):
        raise LedgerError("latest publication identity does not match its immutable epoch")
    return publication


def current_greenkeeper():
    from delivery_assurance import command_succeeded, load_command_results
    from ledger_common import LedgerError, load_json, scope_fingerprint
    from validate_checkpoint import _validate_green_keeper_cycle

    publication = current_publication()
    subject = publication["commit"]
    observed = (
        subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "rev-parse", "HEAD", publication["tag"]], cwd=ROOT
        )
        .decode("ascii")
        .splitlines()
    )
    if observed != [subject, subject]:
        raise LedgerError("current immutable publication identity differs")
    folders = sorted((CHECKPOINT / "published-green-keeper").glob("run-*"))
    if not folders:
        raise LedgerError("current complete public Green Keeper is absent")
    folder = folders[-1]
    receipt = load_json(folder / "RECEIPT.json")
    if (
        receipt.get("subjectCommit") != subject
        or receipt.get("subjectTag") != publication["tag"]
        or receipt.get("sourceFingerprint") != scope_fingerprint(ROOT)
        or publication.get("sourceFingerprint") != receipt.get("sourceFingerprint")
        or receipt.get("result") != "PASS"
        or receipt.get("allMandatoryGatesRequested") is not True
        or receipt.get("gateSelectionOverride") is not False
        or receipt.get("localPrivateRefsFilteredOrChanged") is not False
        or receipt.get("sourceEdited") is not False
        or receipt.get("canonicalEvidenceImported") is not True
        or receipt.get("cloneSourceUnchanged") is not True
        or receipt.get("workingSourceUnchanged") is not True
        or receipt.get("temporaryCloneRemoved") is not True
    ):
        raise LedgerError("latest whole unchanged public cycle has not actually passed")
    original_streams(folder, receipt["execution"])
    imported = (folder / "COMMANDS.jsonl").read_bytes()
    rework = (folder / "REWORK-LOG.jsonl").read_bytes()
    if (
        hashlib.sha256(imported).hexdigest() != receipt["importedCommandsSha256"]
        or not (CHECKPOINT / "COMMANDS.jsonl").read_bytes().startswith(imported)
        or (CHECKPOINT / "REWORK-LOG.jsonl").read_bytes() != rework
    ):
        raise LedgerError("exact original append-only canonical import differs")
    cycles = [json.loads(row) for row in rework.splitlines() if row.strip()]
    errors = []
    if not cycles or cycles[-1].get("result") != "GREEN":
        raise LedgerError("the latest canonical complete cycle is not GREEN")
    cycle = cycles[-1]
    _validate_green_keeper_cycle(ROOT, {}, cycle, errors, closure=True)
    commands = load_command_results(CHECKPOINT)
    for row in cycle["gateResults"]:
        if not command_succeeded(commands.get(row["commandId"], {})):
            errors.append("canonical successful command missing: " + row["commandId"])
    if errors:
        raise LedgerError("; ".join(errors))
    return receipt, cycle, folder.relative_to(CHECKPOINT).as_posix()


def sealed_module(name):
    from ledger_common import LedgerError

    if name not in {
        "complete_functional_acceptance",
        "assemble_verified_progress",
        "audit_documentation",
    }:
        raise LedgerError("only the closed reviewed sealed assembler set may be loaded")
    relative = f"docs/checkpoints/{BASELINE}/audit-harness/{name}.py"
    original = subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "show", f"iacode-checkpoints/{BASELINE}:{relative}"],
        cwd=ROOT,
    )
    path = ROOT / relative
    if path.read_bytes() != original:
        raise LedgerError("never consume a rewritten sealed assembler")
    specification = importlib.util.spec_from_file_location("sealed_" + name, path)
    if specification is None or specification.loader is None:
        raise LedgerError("sealed assembler cannot be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.CHECKPOINT, module.ROOT = CHECKPOINT, ROOT
    return module


def sealed_functional_module():
    return sealed_module("complete_functional_acceptance")


def current_execution():
    from ledger_common import LedgerError, load_json, scope_fingerprint

    receipt, _cycle, _folder = current_greenkeeper()
    module = sealed_functional_module()
    verification, publication, knowledge, command, steps = module.current_execution()
    if publication["publishedCommit"] != receipt["subjectCommit"]:
        raise LedgerError("functional and complete quality subjects differ")
    required_flags = (
        "remoteMainEqualsCommit",
        "sharedProjectUnchanged",
        "ownedComposeProjectRemoved",
        "gitStateAfterVerificationClean",
        "unrelatedContainerIdentitiesAndStatesPreserved",
        "temporaryCloneRemoved",
    )
    if any(publication.get(flag) is not True for flag in required_flags):
        raise LedgerError("actual complete functional transport/isolation/cleanup is required")
    executions = []
    for path in (CHECKPOINT / "full-verifier-executions").glob("*/EXECUTION.json"):
        value = load_json(path)
        if value.get("subjectCommit") == receipt["subjectCommit"]:
            executions.append((path, value))
    if len(executions) != 1:
        raise LedgerError("one exact current native full invocation must resolve")
    path, execution = executions[0]
    if (
        execution.get("sourceFingerprint") != scope_fingerprint(ROOT)
        or execution.get("sourceUnchanged") is not True
        or execution.get("subjectTag") != receipt["subjectTag"]
    ):
        raise LedgerError("complete native functional source changed")
    original_streams(path.parent, execution)
    return verification, publication, knowledge, command, steps


def main():
    from ledger_common import LedgerError, load_json, use_utf8_stdout

    use_utf8_stdout()
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise LedgerError("never rewrite terminal or sealed acceptance evidence")
    current_execution()
    return sealed_functional_module().main()


if __name__ == "__main__":
    raise SystemExit(main())
