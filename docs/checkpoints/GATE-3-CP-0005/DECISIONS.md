# Decisions

## D-01 — Preserve singular and plural sealed finding headings

The audit parser treats `## Finding` and `## Findings` as the same bounded section. The change is
compatibility with an immutable sealed report, not a broader parser or a hand-transcribed finding;
the finding identifier and headline still come from the sealed review document and a regression
test fixes the observed rendering.

## D-02 — Stay within Angular major 22 and update the coordinated release lines

The correction keeps the product on its authorized framework major. All Angular runtime/compiler
packages move together to `22.2.1`; CLI/build move together to `22.2.2`, the newest official npm
releases in their respective Angular 22 lines observed during planning. The lockfile is regenerated
by npm rather than edited by hand.

## D-03 — The scanner and severity policy are immutable inputs to this correction

`M1-F-004` is closed only by changing the dependency graph. Critical and High remain blocking and
an unavailable advisory source remains a failure; no advisory suppression, override or denominator
change is permitted.

## D-04 — Internal assurance does not promote M1

The Green Keeper, Delivery Completeness Validator, internal Red Team and Milestone Closure Auditor
were all executed in this implementing session. Their evidence establishes handoff readiness, but
none is recorded as independent review, independent Red Team or an M1 attestation. A later
fresh-session audit must evaluate the sealed subject and write its own checkpoint.
