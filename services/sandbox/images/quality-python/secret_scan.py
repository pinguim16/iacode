#!/usr/bin/env python3
"""Bounded offline credential-pattern scan for a sandbox workspace."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

IGNORED = frozenset({".git", ".gradle", ".mvn", "build", "dist", "node_modules", "target"})
MAX_FILE_BYTES = 2 * 1024 * 1024
PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*"
        r"[\"']?(?!example\b|placeholder\b|not[_-]?set\b)[-A-Za-z0-9._~+/=:@]{8,}"
    ),
)


def main() -> int:
    findings: list[str] = []
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
            if any(pattern.search(text) for pattern in PATTERNS):
                findings.append(path.as_posix())
    if findings:
        print("QUALITY_SECRET_SCAN=FAIL")
        for path in findings[:100]:
            print(f"credential-shaped content: {path}")
        return 1
    print("QUALITY_SECRET_SCAN=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
