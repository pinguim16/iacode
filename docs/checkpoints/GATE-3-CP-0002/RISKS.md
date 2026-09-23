# Risks — GATE-3-CP-0002 (M1 audit)

The consolidated risk register of milestone `M1`, which no single Gate kept: `GATE-3-CP-0001`
closed `R-G2-002` and said nothing of the other risks `GATE-2-CP-0002` left open (`M1-O-002`). Each
entry below was re-read against the audited tree; where a later Gate closed a risk without saying
so, the closure is stated with its evidence.

## Open

**M1-F-003 — The published history cannot validate GATE-1-CP-0001.** HIGH. Every clean clone of the
remote fails the mandatory `tests` gate, and the only copy of the commit the sealed record names is
an unreachable object on this machine, kept from garbage collection by the local reference
`refs/iacode-preserved/b59d66f9f3f9` (`DECISIONS.md` D-10). Corrective delivery `GATE-3-CP-0003`.
**Do not delete that reference** before the correction is published.

**R-G3-001 — The sandbox service holds the container engine's socket.** HIGH in its own register;
**disposition `ACCEPTED_LOCAL_ARCHITECTURAL_RISK`** for the local MVP. Ten controls were proved from
the running stack and the source (`R-G3-001-REVIEW.json`, 10/10) and attacked (`M1-G`): only the
controller mounts the socket, no child receives it, no request field reaches an engine argument, no
API accepts an engine operation, no port is published, every capability is dropped with no new
privileges, no host mount is possible, the network is the policy's, the tool registry is closed and
only `backend.py` starts a process — the Docker client, with argument vectors. Backlog: a rootless
engine or a restricted socket proxy exposing only create, exec, inspect, list and remove.

**R-G2-009 — A provider credential was shared in a chat transcript during the Gate 2 closure.**
HIGH until rotated. Outside the repository: the history scan of this audit is clean (`cmd-0009`)
and nothing inside the repository can revoke a credential. **Owner action**: rotate the key and set
the new one only in `infra/compose/.env`. This audit cannot verify the rotation and does not claim
it.

**M1-F-001 — A model is never shown the shape of a tool request.** MEDIUM. The configured live model
cannot make a tool request; a stronger one does, intermittently. Carried to the corrective delivery
`GATE-3-CP-0003` (`FINDINGS.json`).

**M1-F-002 — A tool result for a sandboxed request is accepted from the API.** MEDIUM. Carried to
the corrective delivery `GATE-3-CP-0003`.

**R-G3-002 — A container shares the kernel.** MEDIUM. Unchanged; held down by the hardening the
battery re-attacked (`M1-A` to `M1-I`). Backlog: a user-space kernel or micro-VM runtime.

**R-G3-005 — The sandbox image's system packages are not scanned.** MEDIUM. Unchanged.

**R-G3-007 — The pre-push discipline is a practice, not a control.** MEDIUM. Unchanged; every
commit of this audit ran the staged secret scan before its push.

**R-G2-003 — A run's history grows without bound in `run_events`.** MEDIUM. Unchanged. Backlog.

**R-G2-004 — The `Effects` protocol and the activity set can drift apart.** MEDIUM. Held down by
`WorkflowDeterminismTests.test_every_effect_is_an_activity`, green in this audit's verification.

**R-G2-008 — The live evidence depends on the operator's OpenAI account.** MEDIUM. Still true: every
live stage of this audit used it. It is also where `M1-F-001` was observed.

**R-G3-003, R-G3-004, R-G3-006** — the sweep's bound, several large results against the context
bound, no retention of sandbox rows and objects. LOW. Unchanged.

**R-G2-005 — A model that cannot produce the envelope burns its one repair.** LOW in its register;
materialised in this audit, and part of `M1-F-001`, which is where it is now tracked.

**R-G2-006, R-G2-007, R-G2-013** — concurrent bootstrap log noise, terminal state and event in two
commits, an observability check that counts any request. LOW. Unchanged.

**M1-O-003 — A fresh installation starts with an empty model catalog.** LOW. The first live run after
`fresh-install` fails until the operator synchronises the catalog. Backlog: synchronise at start or
state the step where the verification leaves the stack.

## Closed

**R-G3-008 — No live model has driven the sandbox.** Closed by this audit: a live model drove the
sandbox through the gateway (`cmd-0016`), and what it found is `M1-F-001`.

**R-G2-010 — Three ledger controls answer later than they could.** Closed by `GATE 3` Phase 0 (fixes
A, B and C: `LedgerCommandReplayabilityTests`, `GuardrailRegistryResolutionTests`,
`LessonIndexFreshnessTests`), which its register did not say.

**R-G2-011 — A stream opened on a finished run ends after its first page.** Closed by `GATE 3` fix D
(`test_a_terminal_stream_drains_every_page_after_the_cursor`).

**R-G2-012 — A delivered test that can only skip.** Closed by `GATE 3` fix E (`AdrIndexTests`).

**R-G2-002 — GATE 3 could implement the executor on the wrong side of the boundary.** Closed by
`GATE 3`, as its register says, and re-checked here (`R-G3-001-REVIEW.json` C10).
