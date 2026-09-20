# Risks

- CRITICAL: positive external milestone status bypasses internal delivery-assurance gates.
- CRITICAL: external validation is self-assertable without authenticated/resolvable evidence.
- CRITICAL: Green Keeper can PASS an empty gate set.
- CRITICAL: completeness can shrink its own denominator.
- CRITICAL: historical content and tags can be moved together without detection.
- CRITICAL: lesson controls/evidence are typed but not resolved, and nested fields escape the lesson secret scan.
- HIGH: stale or wrong-Gate lesson preflight can be accepted.
- HIGH: command evidence recorded from dirty trees is not reproducible at its declared commit.
- HIGH: CP-0006 sealing chronology and aggregate counts are inconsistent.
- MEDIUM: one canonical lesson provenance locator is inaccurate.

All are product risks. None is classified as environmental or flaky.
