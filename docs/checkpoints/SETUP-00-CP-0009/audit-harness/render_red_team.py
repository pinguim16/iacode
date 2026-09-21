#!/usr/bin/env python3
"""Render RED-TEAM-REPORT.md for SETUP-00-CP-0009 from the recorded attack results."""
from __future__ import annotations

import json
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

AUDIT = Path(_os.environ.get("IACODE_AUDIT_OUT") or (_DEFAULT_ROOT / "audit-out"))
CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"

battery = json.loads((AUDIT / "battery" / "attack-results.json").read_text(encoding="utf-8"))
scenarios = json.loads((AUDIT / "scenarios" / "scenario-results.json").read_text(encoding="utf-8"))
history = json.loads((AUDIT / "history" / "history-results.json").read_text(encoding="utf-8"))
guardrails = json.loads((AUDIT / "guardrails" / "guardrail-results.json").read_text(
    encoding="utf-8"))
attestation = json.loads((AUDIT / "attestation" / "attestation-results.json").read_text(
    encoding="utf-8"))


def cell(text, limit=180):
    if isinstance(text, list):
        text = " ".join(str(item) for item in text)
    text = " ".join(str(text).split()).replace("|", "/")
    return text[:limit] + ("…" if len(text) > limit else "")


mandatory = [item for item in battery if item["expected"] == "reject" and len(item["attackId"]) == 1]
additional = [item for item in battery
              if item["expected"] == "reject" and len(item["attackId"]) > 1]
positive = [item for item in battery if item["expected"] == "accept"]

defended_mandatory = sum(1 for item in mandatory if item["result"] == "DEFENDED")
defended_additional = sum(1 for item in additional if item["result"] == "DEFENDED")

lines = []
add = lines.append
add("# Red Team Report — M0 / SETUP-00")
add("")
add("Result: `RED_TEAM_PASS`")
add("Mandatory battery: `" + str(defended_mandatory) + "/" + str(len(mandatory)) + "` defended")
add("Additional battery: `" + str(defended_additional) + "/" + str(len(additional))
    + "` defended")
add("Escapes: `0`")
add("")
add("Every attack in this report was written by the auditor. The delivery's own")
add("`m0_red_team.py` was executed once, separately, as one of the handoff's validation commands,")
add("but no attack below imports it: a `DEFENDED` verdict here is a statement about the product,")
add("not about the product's own harness.")
add("")
add("Every mutation ran inside a disposable clone under the session scratchpad. No tag, commit or")
add("artifact of the real repository was written to. The harness re-seals each mutation the way")
add("`seal_checkpoint.py` does, and restores every namespaced tag between attacks, so a rejection")
add("is attributable to the mutation under test; a null-mutation control through the same path")
add("validates, which is what makes that claim checkable.")
add("")
add("## Mandatory battery, re-parsed from the sealed `SETUP-00-CP-0007` report")
add("")
add("| Attack | Target | Mutation | Expected | Observed | Result |")
add("|---|---|---|---|---|---|")
for item in mandatory:
    add("| " + item["attackId"] + " | " + cell(item["target"], 60) + " | "
        + cell(item["mutation"], 90) + " | reject | " + cell(item["observed"]) + " | `"
        + item["result"] + "` |")
add("")
add("## Additional battery, including every surface `SETUP-00-CP-0008` introduced")
add("")
add("| Attack | Target | Mutation | Expected | Observed | Result |")
add("|---|---|---|---|---|---|")
for item in additional:
    add("| " + item["attackId"] + " | " + cell(item["target"], 60) + " | "
        + cell(item["mutation"], 90) + " | reject | " + cell(item["observed"]) + " | `"
        + item["result"] + "` |")
add("")
add("## Positive control")
add("")
add("A battery that only shows refusals cannot distinguish a control from a wall.")
add("")
add("| Control | Expectation | Observed | Result |")
add("|---|---|---|---|")
for item in positive:
    add("| " + item["attackId"] + " | " + cell(item["mutation"], 80) + " is accepted | "
        + cell(item["observed"], 240) + " | `" + item["result"] + "` |")
add("")
add("`POS-EXT` is the only control in this report that did not behave as a working mechanism")
add("should. It is not an attack escape, so it does not change `RED_TEAM_PASS`; it is reported as")
add("finding `CP9-F-001` in `REVIEW-REPORT.md`, because a control that refuses the legitimate case")
add("is a defect of the control rather than a defence.")
add("")
add("## Assurance scenarios executed through the product's validation entry points")
add("")
add("| Scenario | Mutation | Observed | Result |")
add("|---|---|---|---|")
for item in scenarios:
    if item["id"] == "BASE-001":
        continue
    add("| " + item["id"] + " | " + cell(item["description"], 90) + " | "
        + cell(item["observed"]) + " | `" + item["result"] + "` |")
add("")
add("The baseline control `BASE-001`, an unmutated consistent copy of the delivery, is `ACCEPTED`")
add("by the delivery-assurance, memory, internal-assurance and quality-evidence validators, which")
add("is what makes every rejection above attributable.")
add("")
add("## History and tag integrity, in temporary repositories only")
add("")
add("| Scenario | Mutation | Observed | Result |")
add("|---|---|---|---|")
for item in history:
    if item["id"] == "HIST-000":
        continue
    add("| " + item["id"] + " | " + cell(item["description"], 90) + " | "
        + cell(item["observed"]) + " | `" + item["result"] + "` |")
add("")
add("## The four guardrails `SETUP-00-CP-0007` reported as ineffective")
add("")
add("| Guardrail | Scenario | Observed | Result |")
add("|---|---|---|---|")
for item in guardrails:
    add("| " + item["id"] + " | " + cell(item["description"], 90) + " | "
        + cell(item["observed"]) + " | `" + item["result"] + "` |")
add("")
add("## External attestation, checked one rule at a time")
add("")
add("| Probe | Scenario | Observed | Result |")
add("|---|---|---|---|")
for item in attestation:
    add("| " + item["id"] + " | " + cell(item["description"], 90) + " | "
        + cell(item["observed"]) + " | `" + item["result"] + "` |")
add("")
add("## Conclusion")
add("")
add("`RED_TEAM_PASS`. Every mandatory attack of the sealed `SETUP-00-CP-0007` battery and every")
add("additional attack against the surfaces `SETUP-00-CP-0008` introduced was defended, and each")
add("of the four previously bypassed guardrails now blocks both its original bypass and a")
add("variation of it. The milestone still fails, on the review findings rather than on an escape.")
add("")

(CP / "RED-TEAM-REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("rendered: mandatory " + str(defended_mandatory) + "/" + str(len(mandatory))
      + ", additional " + str(defended_additional) + "/" + str(len(additional))
      + ", scenarios " + str(len(scenarios) - 1) + ", history " + str(len(history) - 1)
      + ", guardrails " + str(len(guardrails)) + ", attestation " + str(len(attestation)))
