# Diff Summary

Base: `3f730dca1a12245ee8fdf8dfad7a523ed5c1c186` (`SETUP-00-CP-0012`, sealed).

This is an **audit** checkpoint. It judges sealed content and produces none of its own inside the
product. No file under `scripts/`, `tests/`, `docs/` outside `docs/checkpoints/`, `.claude/` or
`prompts/` was changed, no sealed checkpoint was modified, and no historical tag was moved.

## Outside this checkpoint directory

| Path | Change | Why |
|---|---|---|
| `.iacode/anchors/checkpoint-chain.json` | modified | The twelfth integrity anchor, for `SETUP-00-CP-0012`. A checkpoint cannot anchor its own tag, so its successor owes it; refusing to write it is itself a validation failure. |
| `.iacode/attestations/M0-CP-0013.json` | added | The attestation this audit authored about the sealed subject it judged. It names the subject and the commit the subject's tag already resolves to, and never its own commit. |
| `docs/checkpoints/LATEST.md` | modified | Points at this checkpoint. |

Those three are the whole footprint of this audit on the repository outside its own directory. Two
of them are in the delivery-assurance scope, which is why they were written **before** the Green
Keeper, the completeness audit, the internal Red Team and the mirror audit ran: each of those
records a fingerprint of the content it judged, and a file added afterwards would make it stale.

## Inside this checkpoint directory

The audit's own artifacts: the plan and the decisions, the matrix written before execution and
rebuilt from the recorded results, the execution record, the independent derivations of the
subject's expected set and of its evidence, the memory measurement, the mirror probe, the escape
probe, the adversarial battery and its report, the review and milestone reports, and the ordinary
checkpoint documents.

`audit-harness/` holds the instruments, so every result reproduces from a clean clone rather than
from this session. Its readers import neither `policies.py`, `delivery_assurance.py` nor
`lessons.py`: where they agree with the delivery, two independent readers agreed.

## What is deliberately absent

No Gate 0 runtime, no `services/`, `runtime/`, `gateway/` or `sandbox/` tree, and no entry for
`GATE 0` in `.iacode/policies/canonical-requirements.json`. Authoring that specification is the
first deliverable of Gate 0, not of this audit.
