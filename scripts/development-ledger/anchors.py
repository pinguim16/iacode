#!/usr/bin/env python3
"""Tamper-evident integrity anchors for the sealed checkpoint chain.

The M0 audit proved that sealed history was not anchored: moving a namespaced tag and ``HEAD``
together, or rewriting a predecessor and refreshing the dependent hashes, both validated. Nothing
outside the mutable checkpoint content recorded what the sealed objects were supposed to be.

An anchor records, for one sealed checkpoint, the values a later reader can re-derive from Git:

    checkpointId, tag, commit, treeHash, previousCheckpoint, previousAnchorHash

and binds them with ``anchorHash``, a SHA-256 over the canonical JSON of exactly those fields.
Because ``previousAnchorHash`` is part of the digest, the anchors form a chain: changing any
earlier anchor changes every later one.

Trust model, stated honestly
----------------------------
This is *tamper evidence inside the local trust model*, not cryptographic protection against an
attacker with full control of the repository. There is no signature and no external trust anchor:
someone who can rewrite the working tree can also recompute the whole chain. What the anchors do
prevent is the class of failure the audit actually found -- a coordinated tag/content move that
leaves the ledger internally consistent -- because the anchor file is committed in an earlier
checkpoint than the objects it describes, so rewriting history without also rewriting a sealed
predecessor is detected. Any claim stronger than that would be false and is not made anywhere in
this repository. ``docs/CHECKPOINT-PROTOCOL.md`` records the same limit in prose.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, load_json, run_git

ANCHOR_FILE = Path(".iacode") / "anchors" / "checkpoint-chain.json"
TAG_NAMESPACE = "refs/tags/iacode-checkpoints/"

ANCHOR_DIGEST_FIELDS = (
    "checkpointId",
    "tag",
    "commit",
    "treeHash",
    "previousCheckpoint",
    "previousAnchorHash",
)


def anchor_path(root: Path) -> Path:
    return root / ANCHOR_FILE


def anchor_hash(anchor: dict[str, Any]) -> str:
    """SHA-256 over the canonical JSON of the anchored fields, in a fixed order."""
    payload = {field: anchor.get(field) for field in ANCHOR_DIGEST_FIELDS}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load_anchors(root: Path) -> list[dict[str, Any]]:
    path = anchor_path(root)
    if not path.is_file():
        return []
    document = load_json(path)
    anchors = document.get("anchors") if isinstance(document, dict) else None
    if not isinstance(anchors, list):
        raise LedgerError("checkpoint-chain.json must declare an anchors array")
    return [item for item in anchors if isinstance(item, dict)]


def resolve_tag(root: Path, tag: str) -> str | None:
    code, commit = run_git(root, "rev-parse", "--verify", f"{tag}^{{commit}}")
    return commit if code == 0 and commit else None


def commit_tree(root: Path, commit: str) -> str | None:
    code, tree = run_git(root, "rev-parse", "--verify", f"{commit}^{{tree}}")
    return tree if code == 0 and tree else None


def build_anchor(
    root: Path,
    checkpoint_id: str,
    commit: str,
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compute one anchor from the repository, linked to its predecessor."""
    tag = f"{TAG_NAMESPACE}{checkpoint_id}"
    tree = commit_tree(root, commit)
    if tree is None:
        raise LedgerError(f"cannot resolve the tree of {commit} for {checkpoint_id}")
    anchor = {
        "checkpointId": checkpoint_id,
        "tag": tag,
        "commit": commit,
        "treeHash": tree,
        "previousCheckpoint": previous.get("checkpointId") if previous else None,
        "previousAnchorHash": previous.get("anchorHash") if previous else None,
    }
    anchor["anchorHash"] = anchor_hash(anchor)
    return anchor


def sealed_checkpoint_ids(root: Path) -> list[str]:
    """Checkpoint directories that already carry their canonical tag, in tag order."""
    checkpoints = root / "docs" / "checkpoints"
    identifiers = []
    for item in sorted(checkpoints.iterdir()) if checkpoints.is_dir() else []:
        if not item.is_dir():
            continue
        if resolve_tag(root, f"{TAG_NAMESPACE}{item.name}") is not None:
            identifiers.append(item.name)
    return identifiers


def verify_chain(
    root: Path,
    require_sealed: bool = True,
    exclude: set[str] | None = None,
) -> list[str]:
    """Re-derive every anchor from Git and report every divergence.

    Detected: a moved historical tag, a tag pointing at a different commit, an unexpected commit,
    an unexpected tree, a broken link between consecutive anchors, and a sealed checkpoint that has
    no anchor at all.

    ``exclude`` names the checkpoint that is being sealed right now. A checkpoint cannot anchor its
    own tag, because the anchor would have to contain the commit that contains the anchor; the
    successor checkpoint anchors it instead, and ``_validate_anchor_chain`` refuses a checkpoint
    that fails to anchor every sealed predecessor.
    """
    exclude = exclude or set()
    errors: list[str] = []
    try:
        anchors = load_anchors(root)
    except LedgerError as exc:
        return [str(exc)]
    if not anchors:
        sealed = [item for item in sealed_checkpoint_ids(root) if item not in exclude]
        if not sealed:
            return []
        return [
            "no checkpoint integrity anchor is recorded for sealed "
            + ", ".join(sealed)
        ]

    previous: dict[str, Any] | None = None
    for index, anchor in enumerate(anchors):
        identifier = anchor.get("checkpointId") or f"anchor[{index}]"
        tag = anchor.get("tag")
        expected_tag = f"{TAG_NAMESPACE}{anchor.get('checkpointId')}"
        if tag != expected_tag:
            errors.append(f"{identifier}: anchored tag {tag!r} is not the canonical {expected_tag!r}")

        recomputed = anchor_hash(anchor)
        if anchor.get("anchorHash") != recomputed:
            errors.append(
                f"{identifier}: anchorHash does not match its own anchored fields "
                f"(recorded {anchor.get('anchorHash')!r}, recomputed {recomputed!r})")

        expected_previous = previous.get("checkpointId") if previous else None
        expected_previous_hash = previous.get("anchorHash") if previous else None
        if anchor.get("previousCheckpoint") != expected_previous:
            errors.append(
                f"{identifier}: previousCheckpoint {anchor.get('previousCheckpoint')!r} breaks the "
                f"chain; expected {expected_previous!r}")
        if anchor.get("previousAnchorHash") != expected_previous_hash:
            errors.append(
                f"{identifier}: previousAnchorHash breaks the chain with {expected_previous!r}")

        commit = anchor.get("commit")
        resolved = resolve_tag(root, str(tag))
        if resolved is None:
            if require_sealed:
                errors.append(f"{identifier}: anchored tag {tag} does not exist")
        elif resolved != commit:
            errors.append(
                f"{identifier}: tag {tag} resolves to {resolved}, not the anchored commit {commit}")
        if resolved is not None or commit_tree(root, str(commit)) is not None:
            tree = commit_tree(root, str(commit))
            if tree is None:
                errors.append(f"{identifier}: anchored commit {commit} does not exist")
            elif tree != anchor.get("treeHash"):
                errors.append(
                    f"{identifier}: commit {commit} has tree {tree}, not the anchored "
                    f"{anchor.get('treeHash')}")
        previous = anchor

    anchored = {anchor.get("checkpointId") for anchor in anchors}
    if require_sealed:
        for identifier in sealed_checkpoint_ids(root):
            if identifier not in anchored and identifier not in exclude:
                errors.append(f"sealed checkpoint {identifier} has no integrity anchor")
    return errors


def rebuild(root: Path, checkpoint_ids: list[str]) -> dict[str, Any]:
    """Recompute the whole chain from the repository for the given sealed checkpoints."""
    anchors: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for identifier in checkpoint_ids:
        commit = resolve_tag(root, f"{TAG_NAMESPACE}{identifier}")
        if commit is None:
            raise LedgerError(f"{identifier} has no canonical tag to anchor")
        anchor = build_anchor(root, identifier, commit, previous)
        anchors.append(anchor)
        previous = anchor
    return {
        "schemaVersion": "1.0.0",
        "trustModel": (
            "Tamper evident inside the local trust model. The chain detects a moved tag, a "
            "rewritten commit or tree, and a broken link between checkpoints. It is not a "
            "signature and does not defend against an attacker who controls the whole repository."
        ),
        "anchors": anchors,
    }
