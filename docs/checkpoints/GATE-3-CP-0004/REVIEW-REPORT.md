# Review Report — M1 fresh-session milestone re-audit

- Audit checkpoint: `GATE-3-CP-0004`
- Subject: sealed corrective delivery `GATE-3-CP-0003` at `f61f84ca7e830002db1674f1df2aca8172f6e483`
- Milestone: `M1 — IACode V0 foundation` (`GATE 0` through `GATE 3`)
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT` — Codex desktop application, OpenAI, GPT-5, a fresh session independent of the Claude/Anthropic implementing run. This is not a cross-tool milestone verdict.
- Verdict: **`REWORK_REQUIRED`**. `M1-F-004` is Critical. `GATE 4` must not start.

## Executed evidence

The audit froze 23 criteria in `PLAN.md` before substantive execution. It then validated the
integrity chain, remote synchronisation, full history secret scan, every sealed M1 subject locally
and from a transport clone of the authorised remote, every published object named by sealed
evidence, and the ten controls that bound `R-G3-001`.

The complete verification executed all 32 stages. Thirty-one passed, including 711 control-plane
tests, API, gateway, runtime, sandbox and web suites, the real stack, live provider smokes, durable
runtime scenarios, six sandbox scenarios, backup/restore, restart, dependency failure and a clean
fresh installation. Only `dependency-scan` failed (`cmd-0016`).

The first dependency scan reached npm and reported two Critical plus four High advisories; PyPI
timed out. The auditor immediately repeated the exact mandatory scanner. That repetition reached
both sources, found no Python advisories, and reproduced the same npm result (`cmd-0017`,
`DEPENDENCY-SCAN-REPORT.json`). The result is therefore not an availability failure.

## Finding

### M1-F-004 — CRITICAL — The pinned frontend dependency graph contains two Critical and four High advisories

The affected graph names `@angular/build` (Critical, through `piscina`), `@angular/cli` (High,
through `@modelcontextprotocol/sdk`), `@angular/router` (High), `@modelcontextprotocol/sdk` (High),
`piscina` (Critical) and `source-map-js` (High). The advisory classes include a
prototype-pollution/RCE gadget, OAuth credential redirection, and denial of service.

The repository's security policy makes relevant Critical and High advisories blocking. The frozen
AM-17 criterion requires none to remain unresolved, and `PLAN.md` requires the auditor to stop on a
real Critical or High finding. An audit may not update dependencies to turn its own finding green.

Required correction: an implementing checkpoint updates the direct pins and lock graph to versions
with no relevant Critical or High advisories, without suppression or denominator changes, runs the
complete verification with both advisory sources available, seals the result, and submits it to a
new independent M1 audit.

## Stop condition and unexecuted criteria

After the finding reproduced, this audit intentionally did not execute the later cross-gate live
repetition, configured-model repetition, dedicated forged-result probe, audit Red Team, or clean
clone. Their frozen criteria are recorded as `UNVERIFIED`, not passed and not treated as product
failures. Evidence already obtained indicates the previous findings remain corrected: all published
subjects and named commits validate, all 31 non-advisory verification stages pass, the forged-result
scenario embedded in full verification passes 15/15, and `R-G3-001` passes 10/10 controls.

## Verdict

`REWORK_REQUIRED`. The finding is returned to an implementing run as `M1-F-004`; the auditor made
no product change. `M1` remains unpassed and `GATE 4` is prohibited until a corrective delivery is
sealed and a later independent audit grants a milestone pass.

The internal milestone mirror confirms this is the only blocking quality dimension: 15/18 probes
pass, two audit-registry probes are not applicable to an audit checkpoint, and only `MIR-012` fails
because `QUALITY.security` truthfully records the Critical finding. Green Keeper freshness,
completeness, counts, integrity, history and documentation all pass.
