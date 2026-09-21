#!/usr/bin/env python3
"""Independent audit attestations, and the trust boundary between internal and external approval.

The first ``M0`` audit escaped through three doors that were all the same door: a checkpoint could
describe itself as externally validated. Filling ``secondToolValidation`` with syntactically
complete attribution, setting ``milestone.status=PASSED``, and writing ``MILESTONE_EXTERNAL_PASS``
were all accepted, on an intermediate Gate, with the review and the Red Team still pending.

The second ``M0`` audit (``SETUP-00-CP-0009``, finding ``CP9-F-001``) proved that the first repair
had made the honest path impossible. The attestation was consumed as if it belonged to the *subject*
being promoted: the subject's own commit had to appear inside the subject's own tree. No sequence of
repository states satisfies that, so every forgery was refused and no legitimate audit could ever
pass.

The model implemented here separates the two objects that were conflated:

    SUBJECT checkpoint S          sealed, tagged, anchored, immutable, closed at READY_FOR_REVIEW
        |
        | audited by
        v
    AUDIT checkpoint A            a different checkpoint, authored by the auditing run, which
                                  carries .iacode/attestations/<auditId>.json naming S and the
                                  commit S's canonical tag already resolves to
        |
        v
    MILESTONE VERDICT             derived from the attestation, never asserted by either checkpoint

The subject is never rewritten, never re-tagged and never re-sealed to become approved: an audit is
something that happens *to* it, recorded in a later checkpoint. ``derive_milestone_verdict`` answers
"did milestone M pass, and on what evidence" from the repository alone.

Assurance boundary
------------------
An attestation is a file in ``.iacode/attestations/``, so it is inside the delivery-assurance scope
of the checkpoint that writes it -- the audit checkpoint, which runs its gates after writing it. It
is not inside the subject's, because the subject's gates describe the tree its own tag names, which
the later attestation does not change. ``docs/MILESTONE-VALIDATION.md`` records that boundary.

Mechanisms, named honestly
--------------------------
``CROSS_TOOL_INDEPENDENT_AUDIT`` is an audit by a different tool, provider or model.
``FRESH_SESSION_INDEPENDENT_AUDIT`` is an audit by a new session of the same tool, with no memory of
the implementing run, which the owner authorises when cross-tool execution is unavailable. The two
produce different statuses -- ``MILESTONE_EXTERNAL_PASS`` and ``MILESTONE_INDEPENDENT_AUDIT_PASS``
-- because calling the second one "external" would be a claim the evidence does not support.

Trust model, stated honestly
----------------------------
There is no signature and no external key. The control is *structural*, not cryptographic: a verdict
requires a second sealed, tagged, anchored checkpoint authored as an audit of an already sealed
subject, which cannot be produced by editing ``STATE.json`` or one ``secondToolValidation`` field.
An actor who can create that checkpoint and its tag can still forge the relationship; that residual
limit is recorded in ``docs/MILESTONE-VALIDATION.md`` and is never described as cryptographic
assurance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ledger_common import LedgerError, load_json, run_git

ATTESTATION_DIRECTORY = Path(".iacode") / "attestations"

ATTESTATION_SCHEMA_VERSION = "2.0.0"

# Which milestone status each audit mechanism may produce. A fresh-session audit is independent of
# the implementing run but not of the tool, so it may not produce the status that means "another
# tool agreed".
CROSS_TOOL_MECHANISM = "CROSS_TOOL_INDEPENDENT_AUDIT"
FRESH_SESSION_MECHANISM = "FRESH_SESSION_INDEPENDENT_AUDIT"

MECHANISM_STATUSES: dict[str, tuple[str, ...]] = {
    CROSS_TOOL_MECHANISM: ("MILESTONE_EXTERNAL_PASS", "MILESTONE_INDEPENDENT_AUDIT_PASS"),
    FRESH_SESSION_MECHANISM: ("MILESTONE_INDEPENDENT_AUDIT_PASS",),
}

CROSS_TOOL_AVAILABILITY = ("AVAILABLE", "NOT_AVAILABLE")

REQUIRED_FIELDS = (
    "schemaVersion",
    "auditId",
    "milestone",
    "validationMechanism",
    "crossToolValidation",
    "auditorRole",
    "tool",
    "provider",
    "model",
    "freshSession",
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


def statuses_for_mechanism(mechanism: Any) -> tuple[str, ...]:
    """The milestone statuses an audit performed by this mechanism may produce."""
    return MECHANISM_STATUSES.get(str(mechanism), ())


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


def find_attestations_for_milestone(root: Path, milestone: str) -> list[dict[str, Any]]:
    return [item for item in load_attestations(root) if item.get("milestone") == milestone]


def sealed_commit_of(root: Path, checkpoint: str) -> str | None:
    """The commit a checkpoint's canonical tag resolves to, or ``None`` when it is not sealed."""
    from anchors import TAG_NAMESPACE, resolve_tag

    return resolve_tag(root, f"{TAG_NAMESPACE}{checkpoint}")


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    code, _ = run_git(root, "merge-base", "--is-ancestor", ancestor, descendant)
    return code == 0


def _anchored_checkpoints(root: Path) -> set[str]:
    from anchors import load_anchors

    return {str(item.get("checkpointId")) for item in load_anchors(root)}


def verify_attestation(
    root: Path,
    attestation: dict[str, Any],
    subject_checkpoint: str,
    subject_commit: str | None = None,
    *,
    claiming_checkpoint: str | None = None,
) -> list[str]:
    """Every reason this attestation may not be used to grant a milestone verdict.

    ``claiming_checkpoint`` names the checkpoint currently being validated. When it is given, the
    attestation must be the one that checkpoint authored as the audit; the audit checkpoint is then
    not required to be sealed, because it is the content being validated and sealing is post-commit.
    When it is absent the attestation is being read by a third party, and the audit checkpoint must
    itself be sealed under its canonical tag and anchored.
    """
    from anchors import TAG_NAMESPACE, pending_anchor_checkpoint

    label = attestation.get("__path") or attestation.get("auditId") or "attestation"
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if attestation.get(field) in (None, ""):
            errors.append(f"{label}: an independent audit attestation requires {field}")
    if errors:
        return errors

    if attestation.get("schemaVersion") != ATTESTATION_SCHEMA_VERSION:
        errors.append(
            f"{label}: schemaVersion is {attestation.get('schemaVersion')!r}; the attestation "
            f"model that separates the subject from its auditor is "
            f"{ATTESTATION_SCHEMA_VERSION}")

    mechanism = str(attestation.get("validationMechanism"))
    if mechanism not in MECHANISM_STATUSES:
        errors.append(
            f"{label}: validationMechanism is {mechanism!r}; the recognised mechanisms are "
            + ", ".join(sorted(MECHANISM_STATUSES)))
    availability = attestation.get("crossToolValidation")
    if availability not in CROSS_TOOL_AVAILABILITY:
        errors.append(
            f"{label}: crossToolValidation is {availability!r}; it must be one of "
            + ", ".join(CROSS_TOOL_AVAILABILITY))
    elif mechanism == CROSS_TOOL_MECHANISM and availability != "AVAILABLE":
        errors.append(
            f"{label}: a {CROSS_TOOL_MECHANISM} records crossToolValidation=AVAILABLE; "
            f"{availability!r} contradicts the mechanism it claims")
    if mechanism == FRESH_SESSION_MECHANISM and attestation.get("freshSession") is not True:
        errors.append(
            f"{label}: a {FRESH_SESSION_MECHANISM} requires freshSession=true, which is the only "
            f"independence it claims")

    # -- the subject ---------------------------------------------------------------------
    if attestation.get("subjectCheckpoint") != subject_checkpoint:
        errors.append(
            f"{label}: attests checkpoint {attestation.get('subjectCheckpoint')!r}, not "
            f"{subject_checkpoint!r}")
    declared_commit = attestation.get("subjectCommit")
    if subject_commit and declared_commit != subject_commit:
        errors.append(
            f"{label}: attests commit {declared_commit!r}, not the subject commit "
            f"{subject_commit!r}")

    subject_directory = root / "docs" / "checkpoints" / str(attestation.get("subjectCheckpoint"))
    sealed_subject = sealed_commit_of(root, str(attestation.get("subjectCheckpoint")))
    if not subject_directory.is_dir():
        errors.append(
            f"{label}: subject checkpoint {attestation.get('subjectCheckpoint')} does not exist")
    elif sealed_subject is None:
        errors.append(
            f"{label}: subject checkpoint {attestation.get('subjectCheckpoint')} is not sealed "
            f"under {TAG_NAMESPACE}{attestation.get('subjectCheckpoint')}; an audit judges sealed "
            f"content")
    else:
        if declared_commit != sealed_subject:
            errors.append(
                f"{label}: subjectCommit {declared_commit!r} is not the commit "
                f"{TAG_NAMESPACE}{attestation.get('subjectCheckpoint')} resolves to "
                f"({sealed_subject})")
        try:
            if str(attestation.get("subjectCheckpoint")) not in _anchored_checkpoints(root):
                errors.append(
                    f"{label}: subject checkpoint {attestation.get('subjectCheckpoint')} is not in "
                    f"the integrity chain")
        except LedgerError as exc:
            errors.append(f"{label}: {exc}")

    # The subject is the delivery this audit succeeds. Without this rule an actor could attest an
    # old, easy checkpoint and claim the milestone passed on it, because every other check would
    # hold: the old checkpoint is sealed, anchored and an ancestor of everything after it.
    if sealed_subject is not None:
        from anchors import sealed_checkpoints_in_history_order

        sealed_order = sealed_checkpoints_in_history_order(root)
        audited = str(attestation.get("subjectCheckpoint"))
        expected_subject = None
        if claiming_checkpoint is not None:
            # The claiming checkpoint may already be sealed when it is validated, so it is removed
            # before asking which delivery it succeeds; a checkpoint never succeeds itself.
            preceding = [item for item in sealed_order if item != claiming_checkpoint]
            expected_subject = preceding[-1] if preceding else None
        else:
            auditor = str(attestation.get("auditCheckpoint"))
            if auditor in sealed_order:
                position = sealed_order.index(auditor)
                expected_subject = sealed_order[position - 1] if position else None
        if expected_subject is not None and audited != expected_subject:
            errors.append(
                f"{label}: attests {audited}, which is not the sealed checkpoint this audit "
                f"succeeds ({expected_subject}); an audit judges the delivery it follows")

    # -- the auditor ---------------------------------------------------------------------
    audit_checkpoint = str(attestation.get("auditCheckpoint"))
    if audit_checkpoint == str(attestation.get("subjectCheckpoint")):
        errors.append(
            f"{label}: the audit checkpoint and the audited checkpoint are the same; a verdict may "
            f"not be authored by the delivery it judges")
    elif not (root / "docs" / "checkpoints" / audit_checkpoint).is_dir():
        errors.append(f"{label}: audit checkpoint {audit_checkpoint} does not exist")
    elif claiming_checkpoint is not None:
        if audit_checkpoint != claiming_checkpoint:
            errors.append(
                f"{label}: {claiming_checkpoint} claims a milestone verdict from an attestation "
                f"authored by {audit_checkpoint}; a checkpoint may only carry the verdict of the "
                f"audit it performed")
        code, head = run_git(root, "rev-parse", "HEAD")
        if code == 0 and sealed_subject and not _is_ancestor(root, sealed_subject, head):
            errors.append(
                f"{label}: the subject commit {sealed_subject} is not an ancestor of the audit "
                f"checkpoint's history; an audit judges content that already exists")
    else:
        audit_commit = sealed_commit_of(root, audit_checkpoint)
        if audit_commit is None:
            errors.append(
                f"{label}: audit checkpoint {audit_checkpoint} is not sealed under "
                f"{TAG_NAMESPACE}{audit_checkpoint}")
        else:
            try:
                anchored = _anchored_checkpoints(root)
            except LedgerError as exc:
                anchored = set()
                errors.append(f"{label}: {exc}")
            if (audit_checkpoint not in anchored
                    and audit_checkpoint != pending_anchor_checkpoint(root)):
                errors.append(
                    f"{label}: audit checkpoint {audit_checkpoint} is not in the integrity chain")
            if sealed_subject and not _is_ancestor(root, sealed_subject, audit_commit):
                errors.append(
                    f"{label}: the subject commit {sealed_subject} is not an ancestor of the audit "
                    f"commit {audit_commit}; an audit judges content that already exists")

    # -- the verdict ---------------------------------------------------------------------
    if attestation.get("reviewResult") != "APPROVED":
        errors.append(
            f"{label}: reviewResult is {attestation.get('reviewResult')!r}; a milestone PASS "
            f"requires APPROVED")
    if attestation.get("redTeamResult") != "RED_TEAM_PASS":
        errors.append(
            f"{label}: redTeamResult is {attestation.get('redTeamResult')!r}; a milestone PASS "
            f"requires RED_TEAM_PASS")
    for field in ("completeness", "evidenceCoverage"):
        value = attestation.get(field)
        if not isinstance(value, (int, float)) or float(value) != 100.0:
            errors.append(f"{label}: {field} is {value!r}; a milestone PASS requires 100.0")
    if attestation.get("testResult") != "PASS":
        errors.append(
            f"{label}: testResult is {attestation.get('testResult')!r}; a milestone PASS requires "
            f"PASS")

    return errors


def resolve_external_pass(
    root: Path,
    milestone: str,
    subject_checkpoint: str,
    subject_commit: str | None = None,
    *,
    claiming_checkpoint: str | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    """The attestation that authorizes a milestone verdict, or the reasons there is none."""
    try:
        attestation = find_attestation(root, milestone, subject_checkpoint)
    except LedgerError as exc:
        return None, [str(exc)]
    if attestation is None:
        return None, [
            f"no independent audit attestation exists for milestone {milestone} and checkpoint "
            f"{subject_checkpoint}; a milestone verdict may not be self-asserted"
        ]
    return attestation, verify_attestation(
        root, attestation, subject_checkpoint, subject_commit,
        claiming_checkpoint=claiming_checkpoint)


def derive_milestone_verdict(
    root: Path,
    milestone: str,
    subject_checkpoint: str | None = None,
) -> dict[str, Any]:
    """Derive whether a milestone passed, from the sealed repository alone.

    The answer is never read from a status field. It is computed from the attestations a completed
    audit left behind, each of them re-verified against the subject it names, the auditor that
    wrote it, and the four results that make a milestone pass.
    """
    candidates = find_attestations_for_milestone(root, milestone)
    if subject_checkpoint is not None:
        candidates = [
            item for item in candidates if item.get("subjectCheckpoint") == subject_checkpoint]
    evaluated: list[dict[str, Any]] = []
    for attestation in candidates:
        subject = str(attestation.get("subjectCheckpoint"))
        reasons = verify_attestation(
            root, attestation, subject, sealed_commit_of(root, subject))
        evaluated.append({
            "auditId": attestation.get("auditId"),
            "path": attestation.get("__path"),
            "subjectCheckpoint": subject,
            "subjectCommit": attestation.get("subjectCommit"),
            "auditCheckpoint": attestation.get("auditCheckpoint"),
            "validationMechanism": attestation.get("validationMechanism"),
            "crossToolValidation": attestation.get("crossToolValidation"),
            "valid": not reasons,
            "reasons": reasons,
            "permittedStatuses": list(statuses_for_mechanism(
                attestation.get("validationMechanism"))),
        })

    accepted = [item for item in evaluated if item["valid"]]
    if not candidates:
        return {
            "milestone": milestone,
            "status": "NOT_PASSED",
            "reasons": [
                f"no independent audit attestation exists for milestone {milestone}"],
            "attestations": evaluated,
            "accepted": [],
        }
    return {
        "milestone": milestone,
        "status": "PASSED" if accepted else "NOT_PASSED",
        "reasons": [] if accepted else [
            reason for item in evaluated for reason in item["reasons"]],
        "attestations": evaluated,
        "accepted": accepted,
    }
