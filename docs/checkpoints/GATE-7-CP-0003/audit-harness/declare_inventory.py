"""Declare the reviewed corrective scope; reject any unrelated changed path."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import blob_hash, canonical_hash_path, git_delta, load_json, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]

AUTHORED = {
    "scripts/development-ledger/gate4_red_team.py": (
        "HISTORY-TRANSPORT-002 repairs the separately observed host Red Team clone/checkout "
        "and subject-producer child Git scope without global or historical changes."
    ),
    "scripts/development-ledger/ledger_common.py": (
        "Expose the same closed canonical assurance-policy document parser for immutable "
        "self-qualification input validation; no scope policy or denominator change."
    ),
    "scripts/iacode/self_qualification_source.py": (
        "LSN-0154 preserves every immutable non-checkpoint Git blob under unchanged capacity; "
        "all excluded accumulated checkpoint evidence remains separately fully validated."
    ),
    "scripts/iacode/scenarios/quality_engine_e2e.py": (
        "Use the policy-bound immutable product-input view in actual self-qualification; "
        "retain every canonical project/check assertion, deadline and capacity limit."
    ),
    "tests/test_m2_host_transport.py": (
        "Real host caller short/null, long binary transport, unchanged configuration and "
        "genuine refusal controls; no successful producer is simulated."
    ),
    "tests/test_m2_self_snapshot.py": (
        "Real Git complete selection, dirty-state, future project, object identity, policy, "
        "nonregular-input and export-filter controls with unchanged snapshot limits."
    ),
    (
        "docs/adr/ADR-0065-self-qualification-uses-immutable-product-inputs-"
        "not-checkpoint-outputs.md"
    ): ("Record the bounded immutable product-input and separate complete evidence boundary."),
    "apps/api/requirements.txt": "Pin the actual advisory-corrected certificate bundle.",
    "apps/api/requirements.lock.txt": "Regenerate the complete canonical backend lock in Docker.",
    "apps/web/package.json": (
        "Fix actual Vite and Vitest advisories without scanner exceptions or policy changes."
    ),
    "apps/web/package-lock.json": "Regenerate the complete frontend dependency graph canonically.",
    "docs/VERSIONS.md": "Record actual resolved compatibility and security versions with sources.",
    "scripts/development-ledger/derive_counts.py": (
        "IMPORT-ISOLATION-001 restores caller import bindings around real complete unittest "
        "discovery; no approximate count, historical rewrite or consumer-specific preload."
    ),
    "tests/test_m2_discovery_isolation.py": (
        "Real valid null, import leakage, collision, repeated-root, loader and refusal controls."
    ),
    "docs/adr/ADR-0064-unittest-discovery-restores-caller-import-bindings.md": (
        "Record the bounded single-threaded import-binding transaction and its residual limits."
    ),
    "scripts/development-ledger/review_bundle.py": (
        "HISTORY-TRANSPORT-001 extends ADR-0058 per-command long-path handling to actual "
        "transport clone/checkout and ADR-0063 legacy child runtime configuration; "
        "no archive membership, sealed source or global config change."
    ),
    (
        "docs/adr/ADR-0063-historical-review-producers-inherit-only-"
        "process-scoped-git-path-handling.md"
    ): (
        "Record the measured immutable legacy producer process-environment boundary; "
        "no historical subject rewrite or independent approval."
    ),
    "tests/test_m2_history_transport.py": (
        "Actual short-HEAD null, long-path Git materialization and genuine-refusal controls; "
        "missing review producers stay FAIL and are never live reconstruction proof."
    ),
    "tests/test_m2_continuation.py": (
        "LSN-0140 actual corrective/current canonical sections, recorded lesson/guard membership "
        "and original/adverse controls without weakening inherited assertions."
    ),
    "docs/checkpoints/M2-CONSOLIDATION.md": (
        "Distinguish active incomplete CP0003 correction from retained sealed CP0001 history; "
        "preserve M2 independent boundary and no Gate8 authorization."
    ),
    ".gitattributes": (
        "LSN-0131 guarded recurrence: explicit byte-preserving bounda"
        "ries for copied inherited audit originals and current observ"
        "ations; no original normalization or detector exemption."
    ),
    "scripts/development-ledger/new_checkpoint.py": (
        "M2-F-001 literal producer invocation and actual launch directory."
    ),
    "scripts/development-ledger/m0_red_team.py": (
        "Implement the canonically registered independently escaped M"
        "2-RT-01 using actual no-phase/quoted-phase producers and hum"
        "an replay, without narrowing inherited membership."
    ),
    "scripts/development-ledger/audit_runner_bridge.py": (
        "Explicitly approved closed host-runner adapter and exact own"
        "ership cleanup planning, within canonical assurance source s"
        "cope."
    ),
    "scripts/iacode/client_checks.py": (
        "M2-F-002 separate safe raw-byte producer and cleanup observations."
    ),
    "scripts/iacode/gates/client_tests.py": (
        "Report structured fail-closed client execution without masking either observation."
    ),
    "scripts/iacode/native_editor.py": (
        "Extend M2-F-002 through the actual owned native wrapper and "
        "caller without changing process ownership or drain deadlines"
        "."
    ),
    "scripts/iacode/native_execution.py": (
        "Bounded original native producer identity and independent ty"
        "ped process/handle cleanup observations with unchanged succe"
        "ssful interface."
    ),
    "tests/test_m2_audit_corrections.py": (
        "Causal real-child/replay regressions with null/adverse and exact-owner controls."
    ),
    "tests/test_m2_closed_runner_bridge.py": (
        "Real Windows child and adversarial controls for the explicit"
        "ly authorized isolated validation bridge."
    ),
    "tests/test_m2_owned_resource_cleanup.py": (
        "Adversarial ownership, shared-image and unrelated-applicatio"
        "n cleanup plan controls without engine writes."
    ),
    "tests/test_m2_native_observation.py": (
        "Actual owned native producer, privacy, callback, caller and "
        "output-handle failure controls; no editor or Docker launch."
    ),
    "tests/test_m2_bridge_physical_bounds.py": (
        "Actual private-source/report confinement with valid nulls, r"
        "eparse/hardlink controls and a labeled growing-prefix bounda"
        "ry."
    ),
    "tests/test_m2_cleanup_operator.py": (
        "Checkpoint-operator controls using real Python producers and"
        " isolated Docker boundaries; never live engine cleanup accep"
        "tance."
    ),
    "tests/test_m2_current_stream_bootstrap.py": (
        "Cold actual UTF-8 entry-block positive/adverse controls with"
        "out replaying runtime/cleanup main bodies."
    ),
    "tests/test_m2_observation_transport.py": (
        "Real Git archive and both checkout modes for every canonical"
        "ly declared copied observation; actual boundary-removal adve"
        "rse control with valid binary null."
    ),
    "tests/test_m2_bootstrap_ownership.py": (
        "Guard the actual current bootstrap caller and archived adver"
        "se preimage; execute real Windows owned surviving-writer pro"
        "of without Engine operations."
    ),
    "tests/test_m2_progress_publication.py": (
        "Actual publication caller guard and explicitly modeled metad"
        "ata decision controls; real current lint remains separately "
        "required before publication."
    ),
    ".iacode/policies/audit-registry.json": (
        "Bind both M2 findings and escaped attack to corrective requirement derivation."
    ),
    ".iacode/memory/lessons.jsonl": (
        "Escalate guarded recurrences and add actual causal preventio"
        "n; preserve other lesson semantics."
    ),
    ".iacode/memory/guardrails/registry.json": (
        "Extend existing guards without removing historical controls;"
        " canonical JSON formatting only elsewhere."
    ),
    ".iacode/memory/LESSONS.md": (
        "Canonical rendered memory index after recurrence/guardrail updates."
    ),
    ".iacode/memory/retrospectives/GATE-7-CP-0003.md": (
        "Record observed failures and current corrective limits without independent claims."
    ),
    ("docs/adr/ADR-0061-client-verification-preserves-producer-and-cleanup-outcomes.md"): (
        "Structural producer/cleanup and literal invocation contract."
    ),
    ("docs/adr/ADR-0062-isolated-audit-uses-closed-host-validation-jobs.md"): (
        "Authorized closed canonical runner bridge and exact owned-resource cleanup boundary."
    ),
    "docs/adr/README.md": "Index the current structural ADR atomically.",
    "docs/checkpoints/LATEST.md": (
        "Identify the current unsealed corrective checkpoint and CP00"
        "01 as the last valid immutable seal."
    ),
    ".iacode/anchors/checkpoint-chain.json": (
        "Preserve inherited canonical successor anchor for the sealed CP0001 subject."
    ),
    ("docs/audits/M2-ENTRY-BLOCKED-2026-10-21/environment-isolation-0001/REPORT.md"): (
        "Preserve inherited unsealed entry report with only owner-app"
        "roved prose repair, bound by AUTHORIZED-PROSE-DIFF.json."
    ),
}


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    delta = git_delta(ROOT, state["baseCommit"], None)
    buckets = {name: [] for name in ("filesCreated", "filesModified", "filesDeleted")}
    for path, status in sorted(delta.items()):
        if path in AUTHORED:
            reason = AUTHORED[path]
        elif path.startswith("docs/checkpoints/" + CHECKPOINT.name + "/"):
            reason = (
                "Current corrective checkpoint and owned command-produced rep"
                "orts; no independent approval."
            )
        elif path.startswith(("docs/checkpoints/GATE-7-CP-0002/", "docs/audits/")):
            reason = (
                "Preserve inherited failed/unsealed audit or entry evidence, "
                "not acceptance or implementation."
            )
        else:
            raise ValueError("undeclared scope expansion: " + path)
        entry = {"path": path, "reason": reason}
        if path != CHECKPOINT.relative_to(ROOT).as_posix() + "/FILES.json":
            if status in ("A", "M"):
                entry["hashAfter"] = canonical_hash_path(ROOT / path)
            if status in ("M", "D"):
                entry["hashBefore"] = blob_hash(ROOT, state["baseCommit"], path)
        buckets[
            "filesCreated"
            if status == "A"
            else "filesModified"
            if status == "M"
            else "filesDeleted"
        ].append(entry)
    inventory = load_json(CHECKPOINT / "FILES.json")
    inventory.update(buckets)
    inventory["filesRead"] = [
        {"path": path, "reason": "Canonical intake or original finding source."}
        for path in (
            "AGENTS.md",
            "START-HERE.md",
            "docs/DEVELOPMENT-CONTRACT.md",
            "docs/MASTER-PLAN.md",
            "docs/checkpoints/GATE-7-CP-0001/STATE.json",
            "docs/checkpoints/GATE-7-CP-0001/HANDOFF.md",
            "docs/checkpoints/GATE-7-CP-0002/FINDINGS.json",
            "docs/MILESTONE-VALIDATION.md",
            "docs/GATE-7-CHECKLIST.md",
        )
    ]
    write_json(CHECKPOINT / "FILES.json", inventory)
    print("DECLARED_CURRENT_SCOPE " + str({name: len(rows) for name, rows in buckets.items()}))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
