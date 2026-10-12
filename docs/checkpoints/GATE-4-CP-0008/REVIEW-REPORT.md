# Gate 4 fresh-session independent final review

Verdict: **`REWORK_REQUIRED`**.

The immutable subject is `GATE-4-CP-0007` at `e21d30fde473f302d0f8f60b59acf008fa52e250`; its content commit is `c9adc70032584ce8ff3ad52616f9eae6410c805f`.

The product and execution evidence passed: the published verifier completed 42/42 in one invocation; G4-X7 failed closed for a detected secret, scanner unavailability and a legacy tainted object; architecture passed 12/12; 201/201 requirements, 1709/1709 tests, 97/97 guardrails and 13/13 subject Green Keeper gates were independently re-derived.

The subject's 18-dimension internal mirror was recomputed as 17 PASS, 1 justified NOT_APPLICABLE and 0 FAIL. That remains internal subject evidence and is not this session's independent verdict.

`G4-F-004` is HIGH. Two detached published-clone bundle rebuilds were byte-identical and portable, but neither reproduced the digest or size declared by CP0007. The independent Red Team therefore defended 19/20 attacks and attack T escaped over a valid control.

No product correction was made, CP0007 was not rewritten or re-tagged, and Gate 5 was not started.

Critical findings: 0. High findings: 1. Independent review: `REWORK_REQUIRED`.
