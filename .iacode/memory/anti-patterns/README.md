# Anti-patterns

Practices that repeatedly failed here, each with the evidence that they did.

## documented-but-unenforced-control

A rule stated in a protocol document and not implemented in the validator failed twice: the
finalization audit invariant in `SETUP-00-CP-0004` R3, and the blocker consistency rule in RT-01. In
both cases the document was true about intent and false about behaviour.

Countermeasure: `LSN-0003`, `LSN-0004`, and the rule that an important lesson becomes a guardrail.

## verdict-without-execution

A quality dimension carried forward from an earlier checkpoint without re-running the check.

Countermeasure: `LSN-0005`, evidence references resolved by the validator.

## self-certification

The run that implemented the work also declared the work independently reviewed.

Countermeasure: `LSN-0007`, structured cross-tool state, and `READY_FOR_REVIEW` requiring the
independent verdicts to remain pending.

## label-instead-of-invocation

Recording a convenient name for a command rather than the literal, runnable invocation.

Countermeasure: `LSN-0010`, command reproducibility rules and `record_command.py`.
