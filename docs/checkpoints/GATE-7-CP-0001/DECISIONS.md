# Decisions

- Cmd-0046 has one Windows OSError22 opening the existing preflight output; read-only inspection
  finds the original intact, no competing writer or changed path. The identical canonical
  cmd-0047 succeeds without any permission/global setting change. Root cause is not established;
  retain the actual refusal rather than inventing an environmental diagnosis or silently retrying.

- Source inspection of TimestampedEntity's existing writer contract requires incrementing version
  on lifecycle writes. Knowledge terminalization and retention checks now explicitly load/increment
  that field and bind updated_at to the same operation clock. Actual SQL tests assert withdrawal,
  active checking and subsequent purge versions without changing immutable material. This is an
  implementation completion under G7-INT-003, not an invented prior runtime failure.

- Cmd-0027 memory rendering and cmd-0028 schema derivation briefly overlapped despite the serial
  writer contract. Their actual distinct IDs, completion records and outputs are retained; no
  lost/duplicate command or shared output was observed. Subsequent writers await actual exit.
- G7-INT-003 is an incomplete structural integration caught by correct exact assertions. Keep all
  inherited inventory/base-class/cascade checks, append only authorized entities and prove adverse
  mismatches fail; never replace exact equality by a permissive subset to obtain green.

- Start only explicitly authorized Gate7 after actual sealed Gate6 validation; anchor it without
  changing any predecessor. Close this M2 delivery READY_FOR_REVIEW, not INTERNAL_GATE_PASS or an
  independent verdict. Gate8 remains unauthorized.
- ADR-0053 preserves source permissions, denies storage-only experience reuse and requires exact
  project/content-bound reviewed grants. Empty default registry; synthetic fixture permissions
  apply only to isolated validation inputs, never actual user/provider data.
- ADR-0054 chooses a deterministic cited persistent lexical projection with real invalidation,
  retention/rebuild and explicit operational limits; no embeddings, synthesis or execution authority.
- Baseline completes before plan/architecture/behavior changes. Cmd-0006 is a successful129-case
  inherited run, not current whole acceptance or native proof. Its decoded LF-normalized transcript
  is identified as an observation, not original raw byte evidence. Subsequent wrappers must retain
  their own safe raw producer output before interpretation/cleanup.
- One editor patch was refused before applying because it attempted two operations on PLAN.md.
  No partial document rewrite was accepted; a single ordered Update patch then applied. This is an
  authoring-tool refusal, not a failed runtime test, an omitted requirement or a Gate verdict.
- G7-INT-001 is an inherited public-rollup defect, not a license to weaken the original checks.
  Preserve the published README raw bytes and causal refusal, escalate LSN-0117 recurrence1/HIGH,
  derive every current capability title from MASTER-PLAN and retain old assertions. New clean/
  omission/denial/frozen-status/original-object controls plus the complete unchanged inherited
  documentation class pass cmd-0018/0019. This restores local protection, never independent approval.
