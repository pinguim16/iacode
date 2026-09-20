# Definition of Done

Work is done only when all applicable items are evidenced:

- requirement and Gate scope are satisfied without hidden partial behavior;
- baseline, plan, decisions, alternatives, risks, and limitations are recorded;
- implementation and documentation agree;
- automated tests and relevant manual checks ran successfully;
- build, lint, static analysis, security, and performance checks are recorded truthfully;
- no correct test or quality control was weakened to obtain PASS;
- every recorded `PASS` carries a resolvable evidence reference;
- independent review is `APPROVED`;
- Red Team is `RED_TEAM_PASS`;
- the Gate verdict is granted by a run independent of the implementing run;
- secrets scan passes;
- provenance is complete with training denied unless explicitly authorized;
- checkpoint validates, handoff is executable, and next action is exact;
- Git state and Gate status are reconstructible from the repository.

An inapplicable check is `NOT_APPLICABLE` with justification; an unexecuted check is `NOT_EXECUTED`, never PASS.

