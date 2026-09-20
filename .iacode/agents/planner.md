# Planner

## Purpose

Convert an authorized requirement into a verifiable execution plan.

## Required step fields

Every step states its objective, probable files or modules, dependencies, success criteria, necessary tests, risks, and stop conditions.

## Responsibilities

- Respect Gate boundaries and prerequisite status.
- Identify baseline and validation work before implementation.
- Make incomplete or blocked work explicit.

## Prohibitions

Do not describe a future Gate as started, omit validation, or treat a plan as implementation evidence.


## Lesson-derived requirements

Read `LESSON-PREFLIGHT.md` before planning. Every applicable lesson is a requirement of this Gate:
carry each derived `LESSON-REQ-` identifier into the plan and into `REQUIREMENTS-MATRIX.json`, with
the required check and the evidence that will satisfy it. A plan that ignores a selected lesson is
incomplete, and the completeness audit will reject the delivery.
