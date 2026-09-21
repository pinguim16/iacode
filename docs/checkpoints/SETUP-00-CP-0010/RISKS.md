# Risks

## R1 — The trust model of a milestone verdict is structural, not cryptographic

A verdict now requires a second sealed, tagged, anchored checkpoint authored as an audit of an
already sealed subject. An actor who controls the repository can still create that checkpoint and its
tag, and therefore forge the relationship. This is stated in `docs/MILESTONE-VALIDATION.md`, in
`.iacode/attestations/README.md` and in the module itself, and no document claims more. Signed
attestations remain the available upgrade.

## R2 — This delivery is not independently validated

Everything here — the Green Keeper, the completeness audit, the internal Red Team, the internal
mirror audit, the two simulations — is authored by the implementing run, on the same tooling, in the
same session. None of it is independent validation and none of it is recorded as such. The verdict on
`M0` belongs to the next fresh-session audit.

## R3 — The accepted independence is session independence, not tool independence

`FRESH_SESSION_INDEPENDENT_AUDIT` is the mechanism the owner authorised while cross-tool execution is
unavailable. It is weaker than a different tool, provider or model, and the attestation records
`crossToolValidation: NOT_AVAILABLE` so the limit is visible rather than implied.
`MILESTONE_EXTERNAL_PASS` stays reserved for a cross-tool audit.

## R4 — The simulations execute a fixture, not this repository's own future

`promotion_simulation.py` and `successor_durability.py` build disposable repositories with the real
tooling, the real policies and a minimal memory. They prove that the sequences are executable and
that the controls hold through them; they do not prove that this repository's next checkpoint will
be authored correctly.

## R5 — The prose-count control inspects comments and docstrings only

A count inside an ordinary string literal is data, and the Red Team forges one deliberately, so the
control cannot reach there without forbidding its own attacks. A count written into a string that a
report later renders would still escape this specific control, though the derived-count comparison
over checkpoint Markdown would then catch it.

## R6 — `LSN-0030` is recorded without a guardrail

The preflight still presumes an implementing delivery. The lesson is `CONFIRMED`, scoped to audit
runs, and deliberately not `GUARDED`, because no automated control prevents the situation yet. An
audit run must still decide by hand which derived requirements describe it.

## R7 — Registering a second audit widened the mandatory battery's provenance

The mandatory attacks are now re-parsed from every registered audit's sealed report. The two reports
render their tables differently, so the parser accepts both renderings and decides the battery from
the section heading. A future report that names its additional section differently would be read as
mandatory, which fails safe — more attacks required, never fewer — but would surprise its author.
