# Quality Engine

Delivered by `GATE 4 — QUALITY ENGINE`. The service detects a project profile, freezes a quality
plan from canonical policy, dispatches every project command through the Gate 3 sandbox, stores
content-addressed evidence, and derives the verdict from complete resolved results.

The evaluator never starts a process and never accepts a result, evidence body, or verdict from an
HTTP caller. Initial profiles cover Python, Node, TypeScript, Angular, Maven, and Gradle. See
[`docs/runbooks/QUALITY-ENGINE.md`](../../docs/runbooks/QUALITY-ENGINE.md) for operation and limits.
