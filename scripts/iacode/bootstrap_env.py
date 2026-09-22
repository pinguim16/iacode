#!/usr/bin/env python3
"""Create the local Compose environment file, with real local credentials.

``infra/compose/.env.example`` is committed and carries placeholders. This derives ``.env`` from it
and replaces the placeholder credentials with values generated here.

Generating beats asking. A prompt produces either a password somebody typed twice in two different
environments, or — far more often — the placeholder left exactly as it was, which is how a stack
ends up running with ``change-me-before-starting`` as its database password.

Existing values are preserved. Re-running after a new key is added to the example fills in the new
key and leaves the rest alone, so the file does not have to be rebuilt from scratch and the running
stack's credentials do not change underneath it.
"""

from __future__ import annotations

import argparse
import re
import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import ENV_EXAMPLE, ENV_FILE, StackError, log, main_guard

# The keys whose placeholder is replaced with a generated value. The example file marks each one
# with a GENERATED comment, and this tuple is what actually decides: a comment is documentation,
# and a credential left to documentation is a credential nobody generated.
GENERATED_KEYS = (
    "IACODE_POSTGRES_PASSWORD",
    "IACODE_MINIO_ROOT_PASSWORD",
    "IACODE_GRAFANA_PASSWORD",
)

# MinIO's client credentials are the root credentials in this stack, so they must stay identical.
MIRRORED_KEYS = {"IACODE_MINIO_SECRET_KEY": "IACODE_MINIO_ROOT_PASSWORD"}

PLACEHOLDERS = {"change-me-before-starting", "", "changeme"}

# Alphanumeric only. These values are interpolated into a URL, a shell environment and a YAML
# document; a password containing '@', ':' or '/' silently corrupts a connection string, and one
# containing '$' is eaten by Compose's own interpolation.
ALPHABET = string.ascii_letters + string.digits


def generate_secret(length: int = 40) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


def build(example_text: str, existing: dict[str, str]) -> tuple[str, list[str]]:
    """Render the environment file, returning the text and the keys whose value was generated."""
    generated: dict[str, str] = {}
    produced: list[str] = []

    def resolve(key: str, example_value: str) -> str:
        current = existing.get(key)
        if current is not None and current not in PLACEHOLDERS:
            return current
        if key in MIRRORED_KEYS:
            source = MIRRORED_KEYS[key]
            value = generated.get(source) or existing.get(source) or generate_secret()
            generated[key] = value
            produced.append(key)
            return value
        if key in GENERATED_KEYS:
            value = generate_secret()
            generated[key] = value
            produced.append(key)
            return value
        return example_value

    lines: list[str] = []
    for line in example_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines.append(line)
            continue
        key, _, example_value = stripped.partition("=")
        key = key.strip()
        lines.append(f"{key}={resolve(key, example_value.strip())}")

    text = "\n".join(lines) + "\n"

    # The database URL embeds the password, so it has to be rebuilt from the value that was just
    # generated. Leaving the two to be kept in step by hand is how a stack ends up with a URL
    # authenticating against a password that no longer exists.
    values = parse(text)
    credential = values.get("IACODE_POSTGRES_PASSWORD", "")
    user = values.get("IACODE_POSTGRES_USER", "iacode")
    database = values.get("IACODE_POSTGRES_DB", "iacode")
    text = re.sub(
        r"^IACODE_DATABASE_URL=.*$",
        f"IACODE_DATABASE_URL=postgresql+asyncpg://{user}:{credential}@postgres:5432/{database}",
        text,
        flags=re.MULTILINE,
    )
    return text, produced


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="regenerate every credential, even one that is already set")
    parser.add_argument("--print-path", action="store_true", help="print the path and exit")
    arguments = parser.parse_args()

    if arguments.print_path:
        print(ENV_FILE)
        return 0

    if not ENV_EXAMPLE.is_file():
        raise StackError(f"{ENV_EXAMPLE} is missing; the environment cannot be derived")

    existing = {} if arguments.force else (
        parse(ENV_FILE.read_text(encoding="utf-8")) if ENV_FILE.is_file() else {})
    text, produced = build(ENV_EXAMPLE.read_text(encoding="utf-8"), existing)

    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(text, encoding="utf-8", newline="\n")

    # The names, never the values: this output is routinely pasted into an issue.
    if produced:
        log(f"generated local credentials for: {', '.join(sorted(set(produced)))}")
    else:
        log("every credential was already set; nothing was regenerated")
    log(f"wrote {ENV_FILE}")
    log("this file is ignored by Git and is the only place a real credential lives")
    return 0


if __name__ == "__main__":
    main_guard(main)
