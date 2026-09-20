# Definition of Done

Work is done only when all applicable items are evidenced:

- requirement and Gate scope are satisfied without hidden partial behavior;
- baseline, plan, decisions, alternatives, risks, and limitations are recorded;
- implementation and documentation agree;
- automated tests and relevant manual checks ran successfully;
- build, lint, static analysis, security, and performance checks are recorded truthfully;
- no correct test or quality control was weakened to obtain PASS;
- the lesson preflight ran before the Gate and every derived `LESSON-REQ-` requirement is satisfied;
- every confirmed failure of this Gate became a lesson, and every important lesson became a guardrail;
- every requirement of the delivery exists in `REQUIREMENTS-MATRIX.json`, and none is `PARTIAL` or `MISSING`;
- every recorded `PASS` carries a resolvable evidence reference;
- `GREEN_KEEPER_GATE` is `PASS`, with every rework cycle recorded and no unresolved item;
- `DELIVERY_COMPLETENESS_GATE` is `PASS`, with total coverage and every evidence reference resolved;
- readiness and blockage are never claimed at once: `blockedBy` is empty at `READY_FOR_REVIEW`;
- every recorded command is reproducible from its declared working directory;
- independent review is `APPROVED`;
- Red Team is `RED_TEAM_PASS`;
- the Gate verdict is granted by a run independent of the implementing run;
- secrets scan passes;
- provenance is complete with training denied unless explicitly authorized;
- checkpoint validates, handoff is executable, and next action is exact;
- Git state and Gate status are reconstructible from the repository.

An inapplicable check is `NOT_APPLICABLE` with justification; an unexecuted check is `NOT_EXECUTED`, never PASS.

