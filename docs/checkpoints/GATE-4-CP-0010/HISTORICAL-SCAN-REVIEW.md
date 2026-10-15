# Historical scan component review

The stronger shared transport decoder found two additional shapes in the public history, reported
by cmd-0135: a bearer credential shape and a named assignment shape. No matched value is retained.

The introducing source is aedc17a:tests/test_development_ledger.py. The other listed commit,
845c32b, removed/replaced that blob and is not its content snapshot. Exact AST literal comparison
binds both decoded components to test_redactor_replaces_known_shapes at line 157. Both payloads
are alphabet-sequence test markers. The companion authorization-header fixture already has an
explicit reviewed entry. This is fixed redaction-test input, not environment or service credentials.

Only the two observed kind/component digests are added to the reviewed allowlist. No source path,
file, commit, taxonomy kind or different value is excluded. The negative same-kind control still
rejects an encoded prohibited value alongside an approved raw one. History remains unchanged.
HISTORICAL-SCAN-REVIEW.json retains sanitized observations, digests and AST provenance; the complete
history scan must pass after this narrowly scoped review. Training, RAG and distillation stay false.
