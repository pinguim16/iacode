# G4-CP-0004 findings closure

Result: **CLOSED (1/1)**

## G4-F-002 — HIGH — CLOSED

The verifier now owns one checkout-scoped Compose runtime for the entire canonical order: dynamic
published ports, frozen stage environment, build-before-measurement, bounded observation across a
configured Prometheus scrape cycle, and fail-closed cleanup restricted to the owned project.

The published clean-clone run at `a7ad2f53209923f189a786a1fd162dba764b1efa` executed the verifier
once and passed `42/42` in 5604.4 seconds. `infra` passed in 63.0 seconds, `smoke` passed in 14.4
seconds, and both cleanup checks passed. The publication reconciliation records
`verifierRerun: false`; it corrected only the wrapper's canonical field mapping. The original
sealed `40/42` failure and the independent twenty-attack battery, including G4-X7, remain unchanged.

Evidence: commands `cmd-0052` and `cmd-0058`; `VERIFY.json`;
`PUBLISHED-CLEAN-CLONE-REPORT.json`; `ORDER-ISOLATION-PROBE.json`; `ADR-0033`; `LSN-0095` and
`GRD-0096`.
