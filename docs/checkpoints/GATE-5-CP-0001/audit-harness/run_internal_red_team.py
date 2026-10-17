"""Execute fresh inherited and desktop attacks only after actual Green Keeper/completeness."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from delivery_assurance import completeness_scope
from ledger_common import LedgerError, load_json, scope_fingerprint, utc_now, validate_schema, write_json, use_utf8_stdout
from validate_checkpoint import _validate_green_keeper_cycle

DESKTOP_ATTACKS = [
    ("G5-AUTH", "unauthenticated-domain-refused-before-effects", "Unauthenticated alternate domain access", "Refuse before domain effects"),
    ("G5-TOOL-IPC", "closed-ipc-refuses-tool-result", "Submit a client-owned tool result", "Closed IPC refuses execution authority"),
    ("G5-VERDICT-IPC", "closed-ipc-refuses-quality-verdict", "Submit a client-chosen quality verdict", "Closed IPC refuses verdict authority"),
    ("G5-HOST-IPC", "closed-ipc-refuses-shell.exec", "Ask the client IPC to execute a shell tool", "No host execution operation exists"),
    ("G5-SECRET", "secret-upload-refused-before-sql-or-object-persistence", "Upload exact decoded secret-bearing source", "Refuse before SQL/object writes"),
    ("G5-REPLAY", "redis-replay-refusal-survives-api-restart", "Replay authenticated bytes after actual API restart", "Durable Redis replay claim refuses the duplicate"),
    ("G5-CONSENT", "cli-changed-or-wrong-consent-refused-locally", "Mutate with changed or wrong approved digest", "Refuse locally before request"),
    ("G5-TASK-LOSS", "lost-response-has-one-real-persisted-run", "Drop an already accepted task creation response", "One real row, stable identity and no automatic replay"),
    ("G5-TOOL-FORGERY", "authenticated-external-sandbox-result-forgery-refused", "Forge a result for an actual sandbox-executed public request", "Authenticated external submission is still refused"),
    ("G5-QUALITY-LOSS", "actual-quality-response-loss-reconciles-once-without-replay", "Drop an already accepted quality creation response", "One real quality row and read-only reconciliation without replay"),
    ("G5-SIGINT", "actual-cli-sigint-stops-only-local-observation", "Interrupt installed CLI observation while quality runs remotely", "Exit 130 preserves cursor and leaves remote quality running"),
    ("G5-TAMPER", "actual-object-tamper-refused-before-task-persistence", "Corrupt the actual stored snapshot object", "Digest refusal precedes new task persistence"),
]


def execute(arguments: list[str]) -> dict:
    result = subprocess.run([sys.executable, *arguments], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", check=False)
    return {"command": "python " + subprocess.list2cmdline(arguments),
            "exitCode": result.returncode, "outputTail": result.stdout[-2000:] + result.stderr[-1000:]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", type=Path, required=True)
    args = parser.parse_args()
    destination = CHECKPOINT / "M2-INTERNAL-RED-TEAM.json"
    if destination.exists():
        raise LedgerError("preserve the previous Red Team before any fresh execution")
    fingerprint = scope_fingerprint(ROOT)
    cycles = [json.loads(line) for line in (CHECKPOINT / "REWORK-LOG.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    if not cycles or cycles[-1].get("result") != "GREEN":
        raise LedgerError("the actual complete Green Keeper must be green before Red Team")
    errors: list[str] = []
    _validate_green_keeper_cycle(ROOT, {}, cycles[-1], errors, closure=True)
    completeness = load_json(CHECKPOINT / "COMPLETENESS-REPORT.json")
    if (errors or completeness.get("result") != "PASS"
            or completeness.get("scopeFingerprint") != scope_fingerprint(ROOT, completeness_scope(ROOT, CHECKPOINT))):
        raise LedgerError("ordered current Green Keeper/completeness prerequisite failed: " + str(errors))
    receipts = []
    inherited = execute(["scripts/development-ledger/gate4_red_team.py", "--write"])
    receipts.append(inherited)
    if not destination.is_file():
        write_json(CHECKPOINT / "RED-TEAM-EXECUTION-FAILURE.json", receipts)
        raise LedgerError("the fresh inherited battery produced no report")
    base = load_json(destination)
    write_json(CHECKPOINT / "M2-INHERITED-RED-TEAM.json", base)
    # Subsequent fresh attempts cannot leave the inherited partial PASS as a complete Gate 5 PASS.
    destination.unlink()
    native_path = ROOT / "var/gate5-red-team-native.json"
    desktop_path = ROOT / "var/gate5-red-team-desktop.json"
    receipts.append(execute(["scripts/iacode/gates/client_tests.py"]))
    receipts.append(execute(["scripts/iacode/native_editor.py", "--report", str(native_path)]))
    receipts.append(execute(["scripts/iacode/scenarios/desktop_e2e.py", "--node", str(args.node.resolve()),
                             "--report", str(desktop_path)]))
    native = load_json(native_path) if native_path.is_file() else {}
    desktop = load_json(desktop_path) if desktop_path.is_file() else {}
    # Explicit canonical JSON projections, not a claim of raw byte/digest archival.
    for path, name in ((native_path, "RED-TEAM-NATIVE.json"), (desktop_path, "RED-TEAM-DESKTOP.json")):
        if path.is_file():
            write_json(CHECKPOINT / name, load_json(path))
    write_json(CHECKPOINT / "RED-TEAM-EXECUTIONS.json", receipts)
    steps = {row["name"]: row for row in desktop.get("steps", [])}
    clean = (all(row["exitCode"] == 0 for row in receipts)
             and base.get("baselineControl", {}).get("result") == "VALID"
             and desktop.get("result") == native.get("result") == "PASS"
             and desktop.get("sourceFingerprint") == fingerprint
             and desktop.get("ownedTemporaryDirectoryRemoved") is True
             and native.get("ownedTemporaryDirectoryRemoved") is True
             and steps.get("actual-new-host-secretstorage-recovery-provider-sandbox-quality", {}).get("result") == "PASS")
    attacks = list(base["attacks"])
    for identifier, name, mutation, expected in DESKTOP_ATTACKS:
        observed = steps.get(name, {})
        defended = observed.get("result") == "PASS" and clean
        attacks.append({"attackId": identifier, "description": mutation, "target": "real desktop runtime boundary",
            "mutation": mutation, "expectedDefense": expected,
            "observed": name + ": " + observed.get("result", "NOT_EXECUTED"),
            "result": "DEFENDED" if defended else "ESCAPED", "mandatory": True,
            "origin": "Fresh same-session internal Gate 5 Red Team after Green Keeper/completeness",
            "evidence": ["checkpoint:RED-TEAM-DESKTOP.json", "checkpoint:RED-TEAM-EXECUTIONS.json"]})
    trust = [row for run in native.get("runs", []) for row in run["steps"]
             if row["name"] == "actual-untrusted-workspace-refuses-every-mutation-before-connection"]
    attacks.append({"attackId": "G5-NATIVE-TRUST", "description": "Mutate an actual untrusted workspace",
        "target": "real VS Code workspace trust", "mutation": "Invoke every mutation before connection in an untrusted native host",
        "expectedDefense": "No connection or mutation, while clean trusted hosts complete the real workflow",
        "observed": "actual untrusted refusal count=" + str(len(trust)),
        "result": "DEFENDED" if clean and len(trust) == 1 and trust[0]["result"] == "PASS" else "ESCAPED",
        "evidence": ["checkpoint:RED-TEAM-NATIVE.json", "checkpoint:RED-TEAM-DESKTOP.json"],
        "mandatory": True, "origin": "Fresh actual native host, not an editor API double"})
    unchanged = scope_fingerprint(ROOT) == fingerprint
    escaped = sum(row["result"] != "DEFENDED" for row in attacks)
    report = {"schemaVersion": "1.1.0", "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(),
        "targetFingerprint": fingerprint,
        "source": "Fresh inherited canonical false-PASS battery plus fresh complete client decisions, actual native trust and real desktop runtime attacks; same-session internal only.",
        "baselineControl": {"result": "VALID" if clean and unchanged else "INVALID",
                            "detail": "Actual inherited null mutation plus fresh successful trusted native/provider/sandbox/quality workflow and unchanged source; no assertion-only control.",
                            "evidence": ["checkpoint:M2-INHERITED-RED-TEAM.json", "checkpoint:RED-TEAM-DESKTOP.json"]},
        "attacks": attacks, "total": len(attacks), "defended": len(attacks) - escaped,
        "escaped": escaped, "mandatoryTotal": len(attacks), "mandatoryDefended": len(attacks) - escaped,
        "result": "RED_TEAM_PASS" if not escaped and clean and unchanged else "RED_TEAM_FAIL"}
    errors = validate_schema(report, load_json(ROOT / ".iacode/schemas/red-team-report.schema.json"))
    if errors:
        raise LedgerError("actual Red Team report schema refused: " + str(errors))
    write_json(destination, report)
    lines = ["# Gate 5 internal Red Team", "", "Same-session audit only; no independent verdict.", "",
             "Result: " + report["result"], "", "| Attack | Observed | Result |", "|---|---|---|"]
    lines += [f"| {row['attackId']} | {row['observed'].replace('|', '/')} | {row['result']} |" for row in attacks]
    (CHECKPOINT / "RED-TEAM-REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"INTERNAL_RED_TEAM={report['result']} defended={report['defended']}/{report['total']} control={report['baselineControl']['result']}")
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
