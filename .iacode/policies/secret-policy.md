# Secret Policy

Secrets and authentication material must never enter the Engineering Ledger. The redactor and validator cover authorization headers, bearer credentials, API-key assignments, token assignments, secret assignments, password assignments, DevWorld-style live credentials, OpenAI-style secret keys, GitHub credentials, and private SSH key blocks.

Detected values are replaced with `[REDACTED]`; the original value is never logged. A checkpoint containing an unredacted match is invalid.

## Public history

The repository is pushed to a public remote (`ADR-0024`), so a credential in any commit is a
disclosure. `python scripts/development-ledger/secret_scan.py` applies the canonical patterns plus
wider history patterns — PKCS#8 and PGP private key blocks, cloud access key identifiers, Google and
Slack keys, Anthropic keys, and credentials embedded in a URL's userinfo:

- `--history` scans every reachable blob, commit message and annotated tag message, and is
  mandatory before the history is first made public;
- `--staged` scans the content about to be committed, and precedes every push.

A finding reports the commit, path, line and kind, never the value. A value that is shaped like a
credential and has been reviewed as not being one is listed in
`.iacode/policies/secret-scan-allowlist.json` by the SHA-256 of its secret component, with the
reason; it is still counted in every report, and adding an entry is a reviewed policy change.

## Sandboxes

No credential of any kind enters a sandbox: no provider key, no Git credential, no SSH agent, no
cloud credential and no Docker endpoint. A sandbox receives only the environment variables its
policy names, and the policy may not name a credential.

