# Retrospective — GATE 4 — QUALITY ENGINE / GATE-4-CP-0001

This retrospective records concise repository evidence, decisions and consequences. It contains no
private chain-of-thought, personal data or secret.

## What went well

**The Quality Engine was exercised through its real boundary.** The final verifier ran the API,
Temporal workers, PostgreSQL, MinIO, the Gate 3 sandbox service and the container engine. PASS,
FAIL, IACode, reproduction, restart, cancellation and timeout all traversed that path. Evidence:
`docs/checkpoints/GATE-4-CP-0001/VERIFY.json`, `cmd-0207`.

**False PASS became an executable adversarial property.** Missing results, changed exit status,
forged evidence, changed policy or snapshot, wrong origin, timeout, denial, cancellation and unknown
status were all rejected while the unmutated control remained valid. Evidence: verifier stage
`quality-false-pass`, `scripts/development-ledger/gate4_red_team.py`.

**Failures stayed visible.** Failed reports were preserved before reruns, including the initial
IACode failures, false PASS, fixture packaging failure and the first complete verifier failure.
Evidence: `docs/checkpoints/GATE-4-CP-0001/*-FAIL-*.json`,
`docs/checkpoints/GATE-4-CP-0001/VERIFY-FAIL-CMD-0105.json`.

**Every confirmed failure class received a guardrail.** Thirty-one Gate 4 lessons, `LSN-0060` through
`LSN-0090`, are `GUARDED`; the latest lesson validation reported 90 active lessons and 87 guarded
lessons overall. Evidence: `.iacode/memory/lessons.jsonl`,
`.iacode/memory/guardrails/registry.json`, `cmd-0248`.

**The complete denominator finished green.** The final run passed 42/42 stages, including 746
canonical tests, 137 API tests, 231 gateway tests, 197 agent-runtime tests, 146 sandbox tests, 60
evaluator tests, 49 web tests and all live operational scenarios. Evidence:
`docs/checkpoints/GATE-4-CP-0001/VERIFY.json`.

## What failed

**Persistence ordering and ownership were initially underspecified.** Real PostgreSQL exposed child
facts written before parents, domain-crossing identifiers and cancellation ordering defects. These
became `LSN-0060` through `LSN-0067` and permanent store/workflow controls.

**Project detection, planning and offline images disagreed at their boundaries.** Bounded parsing,
polyglot roots, nested fixtures, toolchain preparation, offline build backends and projected
configuration produced real failures. These became `LSN-0068` through `LSN-0076`.

**The verification harness had stale or incomplete denominators.** Workload waits, commit
resolution, unit discovery, stale reports, test identifiers, ephemeral evidence, UTF-8 output and
source-layout assertions each failed under the complete suite. These became `LSN-0077` through
`LSN-0086`.

**Purpose-built workers and built-image tests drifted from shared contracts.** The durability worker
omitted quality activities, a container test assumed host paths, and unsupported project profiles
were collapsed with operational planning errors. These became `LSN-0087` through `LSN-0089`.

**A repository control depended on an ignored workstation file.** The first internal mirror passed
all earlier dimensions but its clean-clone suite exposed that the evaluator Compose isolation test
used `.env` instead of the versioned `.env.example`. This became `LSN-0090` and `GRD-0091`.

## What repeated

The stale-image failure class from `LSN-0036` recurred when the durability rehearsal used a cached
worker image. It was escalated as a guardrail failure, the rehearsal was changed to rebuild, and
the generalized control now checks every purpose-built rehearsal worker. Evidence: `LSN-0087`,
`GRD-0088`, `AGENT-DURABILITY.json`.

The packaging/environment failure class from `LSN-0074` recurred when flat-layout fixtures were
installed without explicit package metadata. It was escalated rather than repaired silently; all
fixtures now execute inside the no-network quality image. Evidence: `LSN-0074`, `GRD-0075`,
`QUALITY-RECOVERY-PACKAGING-FAIL-CMD-0173.json`.

The discovery-scope failure class from `LSN-0079` recurred when the planner ignored root-level test
files while the runner executed them. The planner and runner now share the supported test-source
scope. Evidence: `LSN-0079`, `GRD-0080`, `QUALITY-FALSE-PASS-CMD-0161.json`.

## What was learned

- Durable orchestration must distinguish domain non-applicability from operational failure and map
  every operational error into a taxonomy that can persist a terminal state.
- A purpose-built worker implements the whole workflow contract, including branches expected to be
  not applicable for its fixture.
- A test executing inside an image may consume only sources declared by that image's build boundary.
- A quality planner and its runner must agree on project roots, test discovery and toolchain identity.
- Complete verification must delete stale stage reports before execution and preserve every new red
  result before a rerun.
- A clean-clone control must name only versioned configuration inputs, even when an ignored local
  file is conventionally present in the implementing workspace.

## What should remain guardrails

| Failure class | Lessons | Guardrails | Permanent evidence |
|---|---|---|---|
| persistence, identity and lifecycle ordering | `LSN-0060`–`LSN-0067` | `GRD-0061`–`GRD-0068` | evaluator persistence/workflow tests and real lifecycle scenarios |
| detection, planning and offline toolchains | `LSN-0068`–`LSN-0076` | `GRD-0069`–`GRD-0077` | evaluator and sandbox image tests |
| verification, evidence and harness truth | `LSN-0077`–`LSN-0086` | `GRD-0078`–`GRD-0087` | Gate 4 repository controls and complete verifier |
| rehearsal activities, image inputs and applicability | `LSN-0087`–`LSN-0089` | `GRD-0088`–`GRD-0090` | Gate 4 guards plus real coding/durability scenarios |
| clean-clone configuration hermeticity | `LSN-0090` | `GRD-0091` | versioned Compose environment control plus internal mirror |

## New lessons

`LSN-0060` through `LSN-0090` were created by this Gate and are all `GUARDED`. Their individual
symptom, root cause, repair, prevention control, evidence, applicability and provenance are recorded
in `.iacode/memory/lessons.jsonl`; this retrospective does not duplicate or narrow those records.

## Updated lessons

The recurrences of `LSN-0036`, `LSN-0074` and `LSN-0079` were escalated in their lesson records and
generalized controls rather than treated as new isolated fixes.

## Retired lessons

No lesson was retired by Gate 4.
