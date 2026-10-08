# Plan — GATE-3-CP-0005, the M1 dependency corrective delivery

An implementing run. It corrects the single Critical finding of the fresh-session `M1` audit
`GATE-3-CP-0004` (`M1-CP-0004`, `REWORK_REQUIRED`) and nothing else: no product capability, no
future project-registry or model-federation work, and no `GATE 4`. It closes at
`READY_FOR_REVIEW`; `M1` remains unpassed until a later fresh-session audit judges the sealed
correction.

## Inputs and baseline

- The sealed audit is registered in `.iacode/policies/audit-registry.json`; the requirement set is
  139 canonical `GATE 3` rows, 56 applicable lesson requirements and `M1-F-004`: 196 rows.
- The sealed report uses `## Finding` for its single finding. The canonical parser previously
  recognised only the plural heading; a compatibility test now holds both sealed renderings fixed
  so the audit cannot disappear from the denominator.
- Two independent baseline executions reached both advisory sources. PyPI has zero findings; npm
  has two Critical and four High findings through `@angular/build`, `@angular/cli`,
  `@angular/router`, `@modelcontextprotocol/sdk`, `piscina` and `source-map-js`.
- Official npm metadata identifies `22.2.1` as the newest coordinated Angular framework/compiler
  release in major 22 and `22.2.2` as the newest CLI/build release in major 22.

## Work, in order

1. **Freeze the audit requirement.** Keep `M1-F-004` derived from the sealed review, record
   `LSN-0057`, and preserve the failed baseline as evidence. Do not alter the advisory scanner or
   its Critical/High denominator.
2. **Update the pinned graph.** Move every direct Angular runtime and compiler package together to
   `22.2.1`, move `@angular/cli` and `@angular/build` together to `22.2.2`, and regenerate only
   `apps/web/package-lock.json` with npm 12 on Node 22.23.2. Review the resulting peer graph and the
   transitive paths that previously carried the advisories.
3. **Prove the correction.** Run the unchanged dependency scanner until both sources are
   `SCANNED` and npm reports zero Critical and High findings. Run npm's own audit, the web build,
   unit tests and lint against the regenerated lock. Add one structural test that fails if the
   scanner stops blocking Critical or High findings or stops failing closed on an unavailable
   source; then promote `LSN-0057` to `GUARDED` as `GRD-0058`.
4. **Close the finding.** Produce `M1-CP-0004-FINDINGS-CLOSURE.json` with the baseline, changed pins,
   clean advisory report, targeted tests and immutable evidence. Update all 196 requirements with
   truthful status and resolvable evidence.
5. **Delivery assurance.** Run full verification, Green Keeper until every mandatory gate is
   green, Delivery Completeness Validator, internal Red Team and Milestone Closure Auditor. Verify
   the remote-history clone, every sealed M1 predecessor, secrets, and the complete checkpoint.
6. **Handoff.** Finalize at `READY_FOR_REVIEW`, commit, seal, push branch and checkpoint tag, verify
   remote synchronization and create the review bundle. The next run must be a fresh independent
   M1 audit; this implementing session cannot grant the milestone verdict.

## Stop conditions

Do not declare `READY_FOR_REVIEW` if either advisory source is unavailable, any relevant Critical
or High finding remains, npm peer resolution is invalid, the web build/tests/lint fail, a mandatory
gate is red, completeness or evidence coverage is below 100%, the internal Red Team or mirror
audit fails, a guardrail failure is unresolved, the clean remote clone fails, or remote state is
unsynchronised. A real external blocker yields `BLOCKED`; a dependency conflict yields rework, not
a scanner waiver or override.

Record an executable plan before implementation.
