# Independent Red Team — M2

Result: **`RED_TEAM_FAIL`**. The complete M2 battery is additionally blocked by unavailable Docker
Engine access.

## Valid executed control and attack

- Baseline control: `VALID`. A fresh public detached subject clone created a checkpoint without an
  optional phase; the generated arguments exactly matched the invocation and the canonical
  reproducibility validator accepted it.
- `M2-RT-01` premise: `VALID`. A separate fresh public clone consumed the unique phase marker into
  `STATE.json`, proving the mutation reached the actual producer.
- Expected: the record contains the supplied `--phase` option/value and replay preserves state.
- Observed: the record omitted both while the canonical validator returned no error.
- Result: `ESCAPED` (1 executed, 0 defended, 1 escape).

The first Red Team attempt is retained as invalid because the auditor harness expected the wrong
default phase. It was not counted. The corrected second attempt used new clones and a valid baseline.

## Blocked battery

Authentication, signed-response, workspace/project isolation, host/sandbox boundary, rights
laundering, secret ingress, corruption, stale citation, retention/resurrection, migrations and
cross-Gate live attacks require the real stack or client container. Engine access was denied before
the audit could own those resources. They remain `BLOCKED`, not defended.

No internal subject Red Team result is used as an independent verdict.
