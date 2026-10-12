#!/usr/bin/env python3
"""Seal a finalized checkpoint: validate the committed content, record it, and tag the result.

Why this tool exists
--------------------
The M0 audit found that the last validation recorded for ``SETUP-00-CP-0006`` described a pre-tag
commit with a dirty working tree, while the checkpoint was sealed at a different commit. The
evidence was true about a moment, and false about the thing it was supposed to describe.

Sealing is therefore a two-step, monotonic, post-commit workflow:

1. the content commit is created by the operator, from a tree that ``finalize_checkpoint.py``
   has already prepared and validated;
2. this tool validates *that commit*, with a clean worktree, and records the run as
   ``post-commit-validation`` bound to it;
3. it stamps the end of the run after that record, refreshes the declared inventory hashes, and
   leaves a second commit containing only the append-only evidence;
4. the canonical tag is created on that second commit.

``validate_checkpoint.py`` then requires the post-commit validation to exist, to have exited zero
over a clean tree, and to describe either ``HEAD`` or ``HEAD^`` -- and, in the second case, that
the difference between them is nothing but the append-only evidence this tool wrote. The residual
limit is stated plainly: the evidence commit is itself validated by the reader and by the next
checkpoint's integrity anchor, because a commit cannot contain a validation of itself.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from ledger_common import (
    LedgerError,
    REVIEW_TRANSPORT_SCHEMA_VERSIONS,
    append_command_record,
    build_command_record,
    canonical_hash_path,
    find_root,
    git_snapshot,
    load_json,
    resolve_latest,
    runtime_label,
    use_utf8_stdout,
    utc_now,
    write_json,
)

TAG_NAMESPACE = "refs/tags/iacode-checkpoints/"

VALIDATOR = "scripts/development-ledger/validate_checkpoint.py"


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--message", default=None, help="message for the evidence commit")
    parser.add_argument("--no-commit", action="store_true",
                        help="record the validation without creating the evidence commit")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    snapshot = git_snapshot(root)
    if snapshot["detached"]:
        print("CHECKPOINT_NOT_SEALED")
        print("- sealing requires an attached branch")
        return 2
    if snapshot["dirty"]:
        print("CHECKPOINT_NOT_SEALED")
        print("- sealing validates committed content; commit the checkpoint first")
        return 2

    # A seal creates the canonical tag, and a sealed checkpoint is later validated from that tag
    # with a detached HEAD. A checkpoint whose state still carries the symbolic HEAD was sealed once
    # (GATE-2-CP-0001, at BLOCKED) and could not be validated from its own tag afterwards: G2-F-013.
    # The state names the tag before anything is sealed.
    canonical_ref = f"{TAG_NAMESPACE}{checkpoint.name}"
    declared_ref = load_json(checkpoint / "STATE.json").get("currentCommit")
    if declared_ref != canonical_ref:
        print("CHECKPOINT_NOT_SEALED")
        print(f"- STATE.json currentCommit is {declared_ref!r}; a sealed checkpoint names its own tag. "
              f"Finalize with --commit-ref {canonical_ref} and commit before sealing")
        return 2

    content_commit = snapshot["head"]
    started = time.monotonic()
    # The canonical tag is created a few lines below, on the evidence commit, so at this moment it
    # does not exist yet. That single relaxation is why this runs in-process with
    # allow_pending_ref: everything else, including the whole secret scan, the inventory and the
    # promotion invariant, is enforced exactly as the standalone validator enforces it afterwards.
    from validate_checkpoint import validate_checkpoint

    errors = validate_checkpoint(root, checkpoint, allow_pending_ref=True, allow_pending_seal=True)
    duration = int((time.monotonic() - started) * 1000)
    exit_code = 1 if errors else 0
    if errors:
        print("CHECKPOINT_INVALID")
        for error in errors:
            print(f"- {error}")
    else:
        print("CHECKPOINT_VALID")

    inputs = [VALIDATOR]
    record = build_command_record(
        root,
        command=f"python {VALIDATOR}",
        arguments=[VALIDATOR],
        purpose=(
            "Validate the sealed checkpoint content as committed, with a clean worktree, so the "
            "final evidence describes the commit the tag will point at."),
        working_directory=str(root),
        runtime=runtime_label("python"),
        inputs=inputs,
        inputs_digest=[{"path": item, "hash": canonical_hash_path(root / item)} for item in inputs],
        result="COMPLETED",
        result_code="OK" if exit_code == 0 else "E_VALIDATION_FAILED",
        exit_code=exit_code,
        duration_ms=duration,
        operation="post-commit-validation",
        phase="seal",
        subject_commit=content_commit,
        commit=content_commit,
        repository_state={
            "branch": snapshot["branch"],
            "head": content_commit,
            "dirty": False,
            "detached": False,
        },
    )
    identifier = append_command_record(checkpoint / "COMMANDS.jsonl", record)
    print(f"[ledger {identifier}] post-commit validation of {content_commit[:12]} "
          f"exit={exit_code}")
    if exit_code != 0:
        print("CHECKPOINT_NOT_SEALED")
        print("- the committed content did not validate; repair the cause and commit again")
        return 1

    state = load_json(checkpoint / "STATE.json")
    if state.get("schemaVersion") in REVIEW_TRANSPORT_SCHEMA_VERSIONS:
        from review_bundle import (
            declaration_from_reconstruction,
            reconstruct_twice_from_transport,
        )

        bundle_started = time.monotonic()
        bundle = root / "artifacts" / "review" / f"{checkpoint.name}.zip"
        reconstruction = reconstruct_twice_from_transport(
            root, checkpoint, content_commit, bundle)
        declaration = declaration_from_reconstruction(
            root, checkpoint, bundle, reconstruction)
        write_json(checkpoint / "REVIEW-BUNDLE-VALIDATION.json", declaration)
        bundle_record = build_command_record(
            root,
            command=(
                "python scripts/development-ledger/review_bundle.py "
                f"--checkpoint {checkpoint.relative_to(root).as_posix()} "
                f"--subject {content_commit} --verify-declaration"
            ),
            arguments=[
                "scripts/development-ledger/review_bundle.py",
                "--checkpoint", checkpoint.relative_to(root).as_posix(),
                "--subject", content_commit,
                "--verify-declaration",
            ],
            purpose=(
                "Reconstruct the finalized content commit twice through non-local Git transport "
                "and bind the byte-identical archive digest and size before creating the seal tag."
            ),
            working_directory=str(root),
            runtime=runtime_label("python"),
            inputs=["scripts/development-ledger/review_bundle.py"],
            result="COMPLETED",
            result_code="OK" if declaration["result"] == "PASS" else "E_RECONSTRUCTION_MISMATCH",
            exit_code=0 if declaration["result"] == "PASS" else 1,
            duration_ms=int((time.monotonic() - bundle_started) * 1000),
            operation="review-bundle-reconstruction",
            phase="seal",
            subject_commit=content_commit,
            commit=content_commit,
            repository_state={
                "branch": snapshot["branch"],
                "head": content_commit,
                "dirty": True,
                "detached": False,
            },
        )
        bundle_identifier = append_command_record(checkpoint / "COMMANDS.jsonl", bundle_record)
        print(
            f"[ledger {bundle_identifier}] transported review reconstruction of "
            f"{content_commit[:12]} result={declaration['result']}"
        )
        if declaration["result"] != "PASS":
            print("CHECKPOINT_NOT_SEALED")
            print("- transported review-bundle reconstructions did not match")
            for index, output in enumerate(reconstruction.get("producerOutput", []), start=1):
                if output:
                    print(f"- reconstruction {index}: {output}")
            return 1

    from finalize_checkpoint import _refresh_inventory_hashes

    metadata = load_json(checkpoint / "RUN-METADATA.json")
    metadata["finishedAt"] = utc_now()
    write_json(checkpoint / "RUN-METADATA.json", metadata)
    write_json(checkpoint / "FILES.json",
               _refresh_inventory_hashes(root, checkpoint, state,
                                         load_json(checkpoint / "FILES.json")))

    if args.no_commit:
        print("CHECKPOINT_SEAL_EVIDENCE_WRITTEN")
        print("Commit the append-only evidence and create the canonical tag.")
        return 0

    message = args.message or f"seal: record the post-commit validation of {checkpoint.name}"
    staged_paths = [
        str((checkpoint / name).relative_to(root)).replace("\\", "/")
        for name in ("COMMANDS.jsonl", "FILES.json", "RUN-METADATA.json")
    ]
    if (checkpoint / "REVIEW-BUNDLE-VALIDATION.json").is_file():
        staged_paths.append(
            str((checkpoint / "REVIEW-BUNDLE-VALIDATION.json").relative_to(root)).replace("\\", "/")
        )
    for argv in (
        ["git", "add", "--", *staged_paths],
        ["git", "commit", "-m", message],
        ["git", "tag", f"iacode-checkpoints/{checkpoint.name}"],
    ):
        result = subprocess.run(argv, cwd=root, text=True, encoding="utf-8",
                                errors="replace", stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False)
        sys.stdout.write(result.stdout)
        if result.returncode != 0:
            print("CHECKPOINT_NOT_SEALED")
            print(f"- {' '.join(argv)} exited {result.returncode}")
            return 1

    print(f"CHECKPOINT_SEALED tag={TAG_NAMESPACE}{checkpoint.name}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
