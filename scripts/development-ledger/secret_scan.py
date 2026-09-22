#!/usr/bin/env python3
"""Scan Git content for credential-shaped values without ever printing one.

The repository is published to a public remote, so a credential that reaches *any* commit is
disclosed the moment that commit is pushed, even if a later commit removed it. Three modes cover
the three moments that matter:

``--history``  every blob reachable from every ref, every commit message and every annotated tag
               message. Mandatory before the first push of the history to a public remote.
``--staged``   the content staged for the next commit. The pre-push check of every later push.
``--tree``     the tracked and untracked-but-not-ignored files of the working tree.

A finding names the commit, the path, the line and the kind of secret, and never the value: the
scanner exists to stop a disclosure and must not become one. A value reviewed as credential-shaped
but not a credential is allowed by the digest of its secret component in
``.iacode/policies/secret-scan-allowlist.json``; it is still counted, never silently dropped.
Exit ``0`` means no blocking finding, ``1`` means at least one, ``2`` means the scan could not run.

    python scripts/development-ledger/secret_scan.py --history
    python scripts/development-ledger/secret_scan.py --staged
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ledger_common import SECRET_PATTERNS, find_root, use_utf8_stdout

# The canonical patterns redact command records and gate the checkpoint tree. A public history
# needs a wider net: key material in formats the canonical set does not name, cloud access key
# identifiers, and credentials embedded in a URL's userinfo. They are kept here rather than added to
# the canonical set so the redaction applied to sealed evidence does not change retroactively.
HISTORY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key block", re.compile(
        r"-----BEGIN (?:ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[0-9A-Za-z-]{10,}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{12,}\b")),
    # A URL whose authority carries `user:password@`. Placeholders a reader is meant to replace
    # are not credentials, and neither is a password made of a template expression.
    ("URL with credentials", re.compile(
        r"\b[a-z][a-z0-9+.-]*://"
        r"(?!(?:user(?:name)?|USER(?:NAME)?|<[^>]+>|\$\{?[A-Za-z_]+\}?|\{[^}]+\}):)"
        r"[^\s:/@'\"<>{}$]+:"
        r"(?!(?:password|PASSWORD|pass|secret|changeme|<[^>]+>|\*+|x+|\$\{?[A-Za-z_]+\}?|\{[^}]+\})@)"
        r"[^\s/@'\"<>{}$]{3,}@[^\s/'\"]+")),
)

ALL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, pattern) for name, pattern, _replacement in SECRET_PATTERNS) + HISTORY_PATTERNS

ALLOWLIST = Path(".iacode") / "policies" / "secret-scan-allowlist.json"

NEWLINE = "\n"
NUL = "\0"
RECORD_SEPARATOR = "\x1e"

Allowlist = frozenset[tuple[str, str]]


@dataclass(frozen=True)
class Finding:
    """One credential-shaped match, located but never quoted."""

    kind: str
    location: str
    path: str
    line: int
    commits: tuple[str, ...]
    allowlisted: bool = False


def secret_component(kind: str, value: str) -> str:
    """The part of a match that would be the credential: a URL's password, otherwise the match."""
    if kind == "URL with credentials":
        return value.split("://", 1)[1].partition(":")[2].partition("@")[0]
    return value


def component_digest(kind: str, value: str) -> str:
    return hashlib.sha256(secret_component(kind, value).encode("utf-8")).hexdigest()


def load_allowlist(root: Path) -> Allowlist:
    """Reviewed ``(kind, digest)`` pairs; a missing policy allows nothing, a malformed one fails."""
    path = root / ALLOWLIST
    if not path.is_file():
        return frozenset()
    document = json.loads(path.read_text(encoding="utf-8"))
    entries = document.get("entries") if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise ValueError(f"{ALLOWLIST.as_posix()}: entries must be a list")
    allowed: set[tuple[str, str]] = set()
    known_kinds = {name for name, _pattern in ALL_PATTERNS}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"{ALLOWLIST.as_posix()}: entry {index} is not an object")
        kind, digest, reason = entry.get("kind"), entry.get("sha256"), entry.get("reason")
        if (kind not in known_kinds or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or not isinstance(reason, str) or not reason.strip()):
            raise ValueError(f"{ALLOWLIST.as_posix()}: entry {index} needs a known kind, "
                             "a sha256 digest and a reason")
        allowed.add((kind, digest))
    return frozenset(allowed)


def scan_text(text: str, allowlist: Allowlist = frozenset()) -> list[tuple[str, int, bool]]:
    """Return ``(kind, line, allowlisted)`` for every pattern match in ``text``."""
    results: set[tuple[str, int, bool]] = set()
    for name, pattern in ALL_PATTERNS:
        for match in pattern.finditer(text):
            allowed = (name, component_digest(name, match.group(0))) in allowlist
            results.add((name, text.count(NEWLINE, 0, match.start()) + 1, allowed))
    return sorted(results, key=lambda item: (item[1], item[0], item[2]))


def _git(root: Path, *arguments: str, data: bytes | None = None) -> bytes:
    completed = subprocess.run(["git", *arguments], cwd=root, input=data, capture_output=True,
                               check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"git {arguments[0]} failed: "
                           f"{completed.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return completed.stdout


def _decode(blob: bytes) -> str | None:
    if b"\x00" in blob[:8192]:
        return None
    return blob.decode("utf-8", errors="replace")


def _read_blobs(root: Path, object_ids: list[str]) -> dict[str, bytes]:
    """Read many blobs through one ``git cat-file --batch`` process."""
    if not object_ids:
        return {}
    payload = _git(root, "cat-file", "--batch",
                   data=(NEWLINE.join(object_ids) + NEWLINE).encode())
    blobs: dict[str, bytes] = {}
    offset = 0
    for object_id in object_ids:
        header_end = payload.index(b"\n", offset)
        parts = payload[offset:header_end].decode().split()
        if len(parts) < 3 or parts[1] == "missing":
            raise RuntimeError(f"object {object_id} could not be read")
        size = int(parts[2])
        start = header_end + 1
        blobs[object_id] = payload[start:start + size]
        offset = start + size + 1
    return blobs


def scan_history(root: Path, allowlist: Allowlist = frozenset()) -> list[Finding]:
    """Scan every blob reachable from every ref, every commit message and every tag message."""
    listing = _git(root, "rev-list", "--objects", "--all").decode("utf-8", "replace")
    paths_by_object: dict[str, set[str]] = {}
    for line in listing.splitlines():
        object_id, _, path = line.partition(" ")
        if path:
            paths_by_object.setdefault(object_id, set()).add(path)
    types = _git(root, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                 data=(NEWLINE.join(paths_by_object) + NEWLINE).encode()).decode()
    blob_ids = [line.split()[0] for line in types.splitlines() if line.endswith(" blob")]

    findings: list[Finding] = []
    for object_id, content in _read_blobs(root, blob_ids).items():
        text = _decode(content)
        if text is None:
            continue
        matches = scan_text(text, allowlist)
        if not matches:
            continue
        commits = tuple(_git(root, "log", "--all", "--format=%h", f"--find-object={object_id}")
                        .decode().split())
        for path in sorted(paths_by_object[object_id]):
            for kind, line_number, allowed in matches:
                findings.append(Finding(kind, "blob", path, line_number, commits, allowed))

    messages = _git(root, "log", "--all", "--format=%h%x00%B%x1e").decode("utf-8", "replace")
    for record in messages.split(RECORD_SEPARATOR):
        commit, _, body = record.strip(NEWLINE).partition(NUL)
        for kind, line_number, allowed in scan_text(body, allowlist):
            findings.append(Finding(kind, "commit-message", "", line_number, (commit,), allowed))

    tag_listing = _git(root, "for-each-ref", "--format=%(objecttype) %(refname)", "refs/tags")
    for line in tag_listing.decode().splitlines():
        object_type, _, reference = line.partition(" ")
        if object_type == "tag":
            body = _git(root, "cat-file", "tag", reference).decode("utf-8", "replace")
            for kind, line_number, allowed in scan_text(body, allowlist):
                findings.append(Finding(kind, "tag-message", reference, line_number, (), allowed))
    return findings


def scan_staged(root: Path, allowlist: Allowlist = frozenset()) -> list[Finding]:
    """Scan the blobs staged for the next commit."""
    listing = _git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    findings: list[Finding] = []
    for path in [item for item in listing.decode().split(NUL) if item]:
        text = _decode(_git(root, "show", f":{path}"))
        if text is None:
            continue
        for kind, line_number, allowed in scan_text(text, allowlist):
            findings.append(Finding(kind, "staged", path, line_number, (), allowed))
    return findings


def scan_tree(root: Path, allowlist: Allowlist = frozenset()) -> list[Finding]:
    """Scan the files the repository carries: tracked, plus untracked and not ignored."""
    listing = _git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    findings: list[Finding] = []
    for path in sorted({item for item in listing.decode().split(NUL) if item}):
        candidate = root / path
        if not candidate.is_file():
            continue
        text = _decode(candidate.read_bytes())
        if text is None:
            continue
        for kind, line_number, allowed in scan_text(text, allowlist):
            findings.append(Finding(kind, "tree", path, line_number, (), allowed))
    return findings


SCANNERS = {"history": scan_history, "staged": scan_staged, "tree": scan_tree}


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--history", action="store_true", help="every reachable blob and message")
    mode.add_argument("--staged", action="store_true", help="the content staged for commit")
    mode.add_argument("--tree", action="store_true", help="the files the repository carries")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument("--root", type=Path, default=None, help="repository root")
    arguments = parser.parse_args(argv)

    mode_name = "history" if arguments.history else "staged" if arguments.staged else "tree"
    try:
        root = (arguments.root or find_root()).resolve()
        findings = SCANNERS[mode_name](root, load_allowlist(root))
    except Exception as exc:  # noqa: BLE001 - every failure to scan is reported as exit 2
        print(f"SECRET_SCAN_ERROR mode={mode_name}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    blocking = [item for item in findings if not item.allowlisted]
    allowed = len(findings) - len(blocking)
    result = "FINDINGS" if blocking else "CLEAN"
    if arguments.json:
        print(json.dumps({"mode": mode_name, "result": result, "blocking": len(blocking),
                          "allowlisted": allowed,
                          "findings": [asdict(item) for item in findings]}, indent=2))
    else:
        for item in blocking:
            commits = ",".join(item.commits) or "-"
            print(f"FINDING kind={item.kind!r} location={item.location} path={item.path or '-'} "
                  f"line={item.line} commits={commits}")
        print(f"SECRET_SCAN_{result} mode={mode_name} findings={len(blocking)} "
              f"allowlisted={allowed}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
