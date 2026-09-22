#!/usr/bin/env python3
"""Prove that the local branch and a checkpoint tag are on the authorised remote.

`ADR-0024`: a Gate claims remote synchronisation only when it is true. "The push printed no error"
is not that proof and neither is ``git log origin/main..main``, which compares against a local
tracking ref that is only as fresh as the last fetch. This asks the remote itself:

- ``origin`` must be the authorised URL;
- the remote ``refs/heads/<branch>`` must name exactly the local branch's commit;
- every ``--tag`` must exist on the remote and name exactly the commit it names locally.

Exit ``0`` means synchronised, ``1`` means not synchronised (the report says what differs), ``2``
means the remote could not be asked, which is an operational blocker and never a pass.

    python scripts/development-ledger/remote_sync.py
    python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0001
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ledger_common import find_root, use_utf8_stdout

AUTHORISED_REMOTE = "https://github.com/pinguim16/iacode.git"
DEFAULT_BRANCH = "main"


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    completed = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, completed.stdout.strip()


def remote_refs(root: Path, remote: str) -> dict[str, str]:
    """Every head and tag the remote advertises, as ``ref -> commit`` (tags peeled)."""
    code, output = _git(root, "ls-remote", "--heads", "--tags", remote)
    if code != 0:
        raise RuntimeError(f"the remote {remote!r} could not be listed")
    refs: dict[str, str] = {}
    for line in output.splitlines():
        commit, _, ref = line.partition("\t")
        if ref.endswith("^{}"):
            refs[ref[:-3]] = commit
        else:
            refs.setdefault(ref, commit)
    return refs


def check(root: Path, remote: str, branch: str, tags: list[str],
          authorised_url: str) -> list[str]:
    """What is not synchronised; empty when everything is."""
    problems: list[str] = []
    code, url = _git(root, "remote", "get-url", remote)
    if code != 0:
        return [f"the remote {remote!r} is not configured"]
    if url != authorised_url:
        problems.append(f"the remote {remote!r} is {url!r}, not the authorised {authorised_url!r}")

    advertised = remote_refs(root, remote)
    code, local_head = _git(root, "rev-parse", f"refs/heads/{branch}")
    if code != 0:
        problems.append(f"the local branch {branch!r} does not exist")
    else:
        remote_head = advertised.get(f"refs/heads/{branch}")
        if remote_head is None:
            problems.append(f"the remote has no branch {branch!r}")
        elif remote_head != local_head:
            problems.append(f"{branch} is {local_head[:12]} locally and "
                            f"{remote_head[:12]} on {remote}")
    for tag in tags:
        reference = tag if tag.startswith("refs/tags/") else f"refs/tags/{tag}"
        code, local_tag = _git(root, "rev-parse", f"{reference}^{{commit}}")
        if code != 0:
            problems.append(f"the tag {reference} does not exist locally")
            continue
        remote_tag = advertised.get(reference)
        if remote_tag is None:
            problems.append(f"the tag {reference} is not on {remote}")
        elif remote_tag != local_tag:
            problems.append(f"the tag {reference} names {local_tag[:12]} locally and "
                            f"{remote_tag[:12]} on {remote}")
    return problems


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--tag", action="append", default=[],
                        help="a tag that must be on the remote at the same commit")
    parser.add_argument("--authorised-url", default=AUTHORISED_REMOTE,
                        help="the URL the remote must have")
    arguments = parser.parse_args(argv)

    root = (arguments.root or find_root()).resolve()
    try:
        problems = check(root, arguments.remote, arguments.branch, arguments.tag,
                         arguments.authorised_url)
    except RuntimeError as exc:
        print(f"REMOTE_SYNC_UNAVAILABLE: {exc}")
        return 2
    for problem in problems:
        print(f"NOT_SYNCHRONISED: {problem}")
    tags = ",".join(arguments.tag) or "-"
    print(f"REMOTE_SYNC_{'FAIL' if problems else 'PASS'} remote={arguments.remote} "
          f"branch={arguments.branch} tags={tags}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
