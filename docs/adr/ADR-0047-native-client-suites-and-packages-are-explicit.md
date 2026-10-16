# ADR-0047 — Native client suites and packages are explicit

- Status: Accepted
- Gate: GATE 5

## Context

Gate 5 adds two dependency-free Node projects and actual Extension Host acceptance. Python's
static case enumerator cannot honestly derive JavaScript or native editor cases. The 1.1 test
registry describes Python collection exclusions correctly but cannot name these frameworks.
The Quality Engine must discover the new projects rather than miss their `.test.cjs` cases.

## Decision

Version the test registry to 1.2.0, add explicit `node-test`, `vscode-extension-host` and
`angular-vitest` frameworks, and retain every existing counted Python suite and exclusion.
Non-Python suites remain explicitly non-counted with a reason; their complete execution is a
mandatory client gate and native live acceptance, never an invented Python case count. A counted
Python guard invokes the real signed-malformed-mutation Node case and asserts it actually ran.
1.0/1.1 subjects retain their historical framework and collection semantics.

The Quality Engine recognizes CommonJS/ESM test suffixes. Mixed Angular repositories keep their
Angular runners while additional plain-Node roots also receive Node build and unit runners.
No old mandatory check or project root is removed. Existing serial-runner arguments are translated
to Node's serial mode; unknown arguments fail rather than selecting fewer cases.

Build the CLI tarball and standard VSIX with a closed file map and Python's standard library.
The versioned manifest, shared core and exact canonical protocol bytes ship together. No install
hook, source workspace, credential, test double, native test harness or downloaded runtime is
packaged. Deterministic package comparison is not installation acceptance: actual npm/VS Code
fresh installation and real runtime workflows are separate mandatory proofs.

## Evidence and alternatives

Cmd-0060 executed 25 complete Node 22 client decision cases and compared two package builds.
It did not execute a native editor or live provider. The standardized VSIX envelope follows
[the VS Code packager format](https://github.com/microsoft/vscode-vsce/blob/main/src/package.ts)
and is judged by actual VS Code installation. Alternatives considered: introducing a runtime
bundler/packager dependency graph, duplicating the core, or silently excluding new suites. The
closed dependency-free build has a smaller surface and a directly testable inventory.

## Consequences, risks and reversal

Package layout and native API compatibility require explicit regression/installation tests.
The project still depends on the declared editor/Node runtime and Docker, not a downloaded hidden
test toolchain. A later dependency requires changing the closed builder and lock/advisory proof.
Reversal restores the previous policy in a new commit only; it never reinterprets sealed subjects.

## Related artifacts

- `docs/adr/ADR-0046-desktop-clients-are-authenticated-runtime-adapters.md`
- `.iacode/policies/test-suites.json`
- `scripts/iacode/build_clients.py`
- `scripts/iacode/gates/client_tests.py`
