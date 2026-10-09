#!/usr/bin/env python3
"""Offline credential scan with only policy-owned, digest-bound false-positive allowances."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

IGNORED = frozenset({".git", ".gradle", ".mvn", "build", "dist", "node_modules", "target"})
MAX_FILE_BYTES = 2 * 1024 * 1024
ALLOWLIST = Path("/opt/iacode/secret-scan-allowlist.json")
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "authorization header",
        re.compile(
            r"(?i)(authorization[\"']?\s*:\s*[\"']?)(?!\[REDACTED\])"
            r"(?:(?:Bearer|Basic)\s+)?[-A-Za-z0-9._~+/=]{6,}"
        ),
    ),
    (
        "bearer credential",
        re.compile(
            r"(?i)\bBearer\s+(?!\[REDACTED\]|credentials?\b|tokens?\b|authentication\b)"
            r"[-A-Za-z0-9._~+/=]{8,}"
        ),
    ),
    (
        "named secret assignment",
        re.compile(
            r"(?i)\b((?:[A-Z0-9]+_)*(?:API_KEY|TOKEN|SECRET|PASSWORD|ACCESS_KEY_ID|"
            r"SECRET_ACCESS_KEY)[\"']?\s*[:=]\s*[\"']?)"
            r"(?!\[REDACTED\]|example\b|placeholder\b|change[_-]?me[_-a-z0-9]*|"
            r"not[_-]?set\b|your[_-])[-A-Za-z0-9._~+/=:@]{6,}"
        ),
    ),
    ("DevWorld credential", re.compile(r"\bdw_live_[A-Za-z0-9_-]{8,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")),
    ("GitHub credential", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    (
        "GitHub fine-grained credential",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    ),
    (
        "private SSH key block",
        re.compile(
            r"-----BEGIN ((?:OPENSSH|RSA|EC|DSA) PRIVATE KEY)-----[\s\S]*?-----END \1-----",
            re.IGNORECASE,
        ),
    ),
    (
        "private SSH key header",
        re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----", re.IGNORECASE),
    ),
    (
        "private key block",
        re.compile(r"-----BEGIN (?:ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
    ),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[0-9A-Za-z-]{10,}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{12,}\b")),
    (
        "URL with credentials",
        re.compile(
            r"\b[a-z][a-z0-9+.-]*://"
            r"(?!(?:user(?:name)?|USER(?:NAME)?|<[^>]+>|\$\{?[A-Za-z_]+\}?|\{[^}]+\}):)"
            r"[^\s:/@'\"<>{}$]+:"
            r"(?!(?:password|PASSWORD|pass|secret|changeme|<[^>]+>|\*+|x+|"
            r"\$\{?[A-Za-z_]+\}?|\{[^}]+\})@)[^\s/@'\"<>{}$]{3,}@[^\s/'\"]+"
        ),
    ),
)


def secret_component(kind: str, value: str) -> str:
    if kind == "URL with credentials":
        return value.split("://", 1)[1].partition(":")[2].partition("@")[0]
    return value


def load_allowlist() -> frozenset[tuple[str, str]]:
    document = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    entries = document.get("entries") if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise ValueError("the policy-owned secret allowlist has no entries array")
    known = {name for name, _pattern in PATTERNS}
    allowed: set[tuple[str, str]] = set()
    for entry in entries:
        kind = entry.get("kind") if isinstance(entry, dict) else None
        checksum = entry.get("sha256") if isinstance(entry, dict) else None
        reason = entry.get("reason") if isinstance(entry, dict) else None
        if (
            kind not in known
            or not isinstance(checksum, str)
            or re.fullmatch(r"[0-9a-f]{64}", checksum) is None
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise ValueError("the policy-owned secret allowlist contains an invalid entry")
        allowed.add((kind, checksum))
    return frozenset(allowed)


def main() -> int:
    try:
        allowlist = load_allowlist()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"QUALITY_SECRET_SCAN=ERROR {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    findings: set[str] = set()
    allowlisted = 0
    for current, directories, filenames in os.walk(".", followlinks=False):
        directories[:] = sorted(name for name in directories if name not in IGNORED)
        for name in sorted(filenames):
            path = Path(current, name)
            if path.is_symlink() or path.stat().st_size > MAX_FILE_BYTES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            for kind, pattern in PATTERNS:
                for match in pattern.finditer(text):
                    checksum = hashlib.sha256(
                        secret_component(kind, match.group(0)).encode("utf-8")
                    ).hexdigest()
                    if (kind, checksum) in allowlist:
                        allowlisted += 1
                    else:
                        findings.add(path.as_posix())
    if findings:
        print("QUALITY_SECRET_SCAN=FAIL")
        for path in sorted(findings)[:100]:
            print(f"credential-shaped content: {path}")
        return 1
    print(f"QUALITY_SECRET_SCAN=PASS allowlisted={allowlisted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
