#!/usr/bin/env python3
"""External audit attestations, and the trust boundary between internal and external approval.

The M0 audit escaped through three doors that were all the same door: a checkpoint could describe
itself as externally validated. Filling ``secondToolValidation`` with syntactically complete
attribution, setting ``milestone.status=PASSED``, and writing ``MILESTONE_EXTERNAL_PASS`` were all
accepted, on an intermediate Gate, with the review and the Red Team still pending.

An external PASS is now derived from an *attestation artifact* produced by a different checkpoint,
never from a field of the checkpoint that benefits from it:

    .iacode/attestations/<auditId>.json

The attestation names the audit, the auditing tool, the subject checkpoint and commit it judged,
the audit checkpoint that carries the evidence, and the four results that make a milestone pass.
Verification re-derives all of it from the repository.

Trust model, stated honestly
----------------------------
There is no signature and no external key. The control is *structural*, not cryptographic:

- the attestation must name an ``auditCheckpoint`` that is not the checkpoint claiming the PASS;
- that audit checkpoint must exist, be sealed under its own canonical tag, and be anchored in the
  integrity chain;
- it must itself record an independent review verdict and a Red Team verdict;
- the attestation must bind the exact ``subjectCommit`` the PASS is claimed for.

So an external PASS can no longer be produced by editing ``STATE.json``, ``QUALITY.json`` or a
single ``secondToolValidation`` field. It requires a second, sealed, tagged, anchored checkpoint
authored as an audit. An actor who can create that checkpoint and its tag can still forge the
relationship; that residual limit is recorded in ``docs/MILESTONE-VALIDATION.md`` and is not
described anywhere as cryptographic assurance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ledger_common import LedgerError, load_json

ATTESTATION_DIRECTORY = Path(".iacode") / "attestations"

REQUIRED_FIELDS = (
    "auditId",
    "milestone",
    "auditorRole",
    "tool",
    "provider",
    "model",
    "subjectCheckpoint",
    "subjectCommit",
    "auditCheckpoint",
    "reviewResult",
    "redTeamResult",
    "completeness",
    "evidenceCoverage",
    "testResult",
    "createdAt",
)


def attestation_directory(root: Path) -> Path:
    return root / ATTESTATION_DIRECTORY


def load_attestations(root: Path) -> list[dict[str, Any]]:
    directory = attestation_directory(root)
    if not directory.is_dir():
        return []
    attestations: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        document = load_json(path)
        if isinstance(document, dict):
            document = dict(document)
            document["__path"] = str(path.relative_to(root)).replace("\\", "/")
            attestations.append(document)
    return attestations


def find_attestation(root: Path, milestone: str, subject_checkpoint: str) -> dict[str, Any] | None:
    for attestation in load_attestations(root):
        if (attestation.get("milestone") == milestone
                and attestation.get("subjectCheckpoint") == subject_checkpoint):
            return attestation
    return None


def verify_attestation(
    root: Path,
    attestation: dict[str, Any],
    subject_checkpoint: str,
    subject_commit: str | None,
) -> list[str]:
    """Every reason this attestation may not be used to grant an external PASS."""
    from anchors import TAG_NAMESPACE, load_anchors, resolve_tag

    label = attestation.get("__path") or attestation.get("auditId") or "attestation"
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if attestation.get(field) in (None, ""):
            errors.append(f"{label}: an external audit attestation requires {field}")
    if errors:
        return errors

    if attestation.get("subjectCheckpoint") != subject_checkpoint:
        errors.append(
            f"{label}: attests checkpoint {attestation.get('subjectCheckpoint')!r}, not "
            f"{subject_checkpoint!r}")
    if subject_commit and attestation.get("subjectCommit") != subject_commit:
        errors.append(
            f"{label}: attests commit {attestation.get('subjectCommit')!r}, not the subject "
            f"commit {subject_commit!r}")

    audit_checkpoint = str(attestation.get("auditCheckpoint"))
    if audit_checkpoint == subject_checkpoint:
        errors.append(
            f"{label}: the audit checkpoint and the audited checkpoint are the same; an external "
            f"verdict may not be authored by the delivery it judges")
    elif not (root / "docs" / "checkpoints" / audit_checkpoint).is_dir():
        errors.append(f"{label}: audit checkpoint {audit_checkpoint} does not exist")
    else:
        tag = f"{TAG_NAMESPACE}{audit_checkpoint}"
        if resolve_tag(root, tag) is None:
            errors.append(f"{label}: audit checkpoint {audit_checkpoint} is not sealed under {tag}")
        else:
            anchored = {item.get("checkpointId") for item in load_anchors(root)}
            if audit_checkpoint not in anchored:
                errors.append(
                    f"{label}: audit checkpoint {audit_checkpoint} is not in the integrity chain")

    if attestation.get("reviewResult") != "APPROVED":
        errors.append(
            f"{label}: reviewResult is {attestation.get('reviewResult')!r}; an external PASS "
            f"requires APPROVED")
    if attestation.get("redTeamResult") != "RED_TEAM_PASS":
        errors.append(
            f"{label}: redTeamResult is {attestation.get('redTeamResult')!r}; an external PASS "
            f"requires RED_TEAM_PASS")
    for field in ("completeness", "evidenceCoverage"):
        value = attestation.get(field)
        if not isinstance(value, (int, float)) or float(value) != 100.0:
            errors.append(f"{label}: {field} is {value!r}; an external PASS requires 100.0")
    if attestation.get("testResult") != "PASS":
        errors.append(
            f"{label}: testResult is {attestation.get('testResult')!r}; an external PASS requires PASS")

    return errors


def resolve_external_pass(
    root: Path,
    milestone: str,
    subject_checkpoint: str,
    subject_commit: str | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    """The attestation that authorizes an external PASS, or the reasons there is none."""
    try:
        attestation = find_attestation(root, milestone, subject_checkpoint)
    except LedgerError as exc:
        return None, [str(exc)]
    if attestation is None:
        return None, [
            f"no external audit attestation exists for milestone {milestone} and checkpoint "
            f"{subject_checkpoint}; an external PASS may not be self-asserted"
        ]
    return attestation, verify_attestation(root, attestation, subject_checkpoint, subject_commit)
