# Secret Policy

Secrets and authentication material must never enter the Engineering Ledger. The redactor and validator cover authorization headers, bearer credentials, API-key assignments, token assignments, secret assignments, password assignments, DevWorld-style live credentials, OpenAI-style secret keys, GitHub credentials, and private SSH key blocks.

Detected values are replaced with `[REDACTED]`; the original value is never logged. A checkpoint containing an unredacted match is invalid.

