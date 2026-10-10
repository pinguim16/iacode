#!/usr/bin/env python3
"""Fresh Gate 4 adversarial audit over canonical false-PASS and bundle mutations."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"
SUBJECT = "GATE-4-CP-0001"
TAG = f"iacode-checkpoints/{SUBJECT}"
EXPECTED_COMMIT = "70a22e824705f414e0c295bbdf89187db9b391f7"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402


def run(argv: list[str], cwd: Path, timeout: float = 3600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def rewrite_zip(source: Path, target: Path, mutate) -> None:  # type: ignore[no-untyped-def]
    with zipfile.ZipFile(source) as archive:
        payload = [(info.filename, archive.read(info.filename)) for info in archive.infolist()]
    payload = mutate(payload)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for name, content in payload:
                archive.writestr(name, content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--raw-report", type=Path, required=True)
    parser.add_argument("--verification-report", type=Path, required=True)
    parser.add_argument("--secret-probe", type=Path, required=True)
    arguments = parser.parse_args()
    scratch = Path(tempfile.mkdtemp(prefix="iacode-g4-red-team-"))
    clone = scratch / "iacode"
    attacks: list[dict[str, object]] = []
    control: dict[str, object] = {"result": "INVALID", "observations": []}
    raw: dict[str, object] = {}
    try:
        cloned = run(["git", "clone", "--quiet", REMOTE, str(clone)], scratch, 900)
        checked = run(["git", "checkout", "--detach", "--quiet", TAG], clone, 300)
        head = run(["git", "rev-parse", "HEAD"], clone, 300).stdout.strip()
        control["observations"] = [
            {"name": "transport clone", "ok": cloned.returncode == 0},
            {"name": "detached subject checkout", "ok": checked.returncode == 0},
            {"name": "subject identity", "ok": head == EXPECTED_COMMIT, "observed": head},
        ]
        if cloned.returncode != 0 or checked.returncode != 0 or head != EXPECTED_COMMIT:
            raise RuntimeError("published subject control could not be established")

        source_env = ROOT / "infra" / "compose" / ".env"
        target_env = clone / "infra" / "compose" / ".env"
        if source_env.is_file():
            shutil.copyfile(source_env, target_env)

        temporary_checkpoint = clone / "var" / "independent-red-team"
        temporary_checkpoint.mkdir(parents=True, exist_ok=True)
        canonical = run(
            [
                sys.executable,
                "scripts/development-ledger/gate4_red_team.py",
                "--checkpoint",
                str(temporary_checkpoint),
                "--write",
                "--skip-gate-rebuild",
            ],
            clone,
            3600,
        )
        raw_path = temporary_checkpoint / "M2-INTERNAL-RED-TEAM.json"
        if raw_path.is_file():
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            arguments.raw_report.resolve().write_text(
                json.dumps(raw, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        canonical_control = (raw.get("baselineControl") or {}).get("result") == "VALID"
        canonical_ok = (
            canonical.returncode == 0
            and raw.get("result") == "RED_TEAM_PASS"
            and canonical_control
            and raw.get("defended") == raw.get("total") == 10
        )
        control["observations"].append({
            "name": "canonical false-PASS null control",
            "ok": canonical_control,
            "detail": raw.get("baselineControl") or (canonical.stdout + canonical.stderr).strip()[-1200:],
        })
        for item in raw.get("attacks") or []:
            attacks.append({
                "attackId": item.get("attackId"),
                "target": item.get("target") or item.get("description"),
                "mutation": item.get("mutation"),
                "expectedDefense": item.get("expectedDefense"),
                "observed": item.get("observed"),
                "result": item.get("result"),
                "source": (
                    "canonical Gate 4 battery executed in the transport clone against the subject "
                    "image rebuilt by the immediately preceding clean-clone verifier"
                ),
            })

        subject_checkpoint = clone / "docs" / "checkpoints" / SUBJECT
        source_bundle = ROOT / "artifacts" / "review" / f"{SUBJECT}-sealed.zip"
        bundle_directory = clone / "var" / "independent-red-team-bundles"
        bundle_directory.mkdir(parents=True, exist_ok=True)
        bundle = bundle_directory / source_bundle.name
        shutil.copyfile(source_bundle, bundle)
        validator = clone / "scripts" / "development-ledger" / "review_bundle.py"

        def validate(candidate: Path) -> subprocess.CompletedProcess[str]:
            return run(
                [
                    sys.executable,
                    str(validator),
                    "--root",
                    str(clone),
                    "--checkpoint",
                    str(subject_checkpoint),
                    "--bundle",
                    str(candidate),
                    "--validate-only",
                ],
                clone,
                900,
            )

        original = validate(bundle)
        original_output = (original.stdout + original.stderr).strip()
        control["observations"].append({
            "name": "unmutated sealed bundle",
            "ok": original.returncode == 0 and "REVIEW_BUNDLE=PASS" in original.stdout,
            "detail": original_output[-1200:],
        })

        mutations = []

        def flip_first_payload(payload):  # type: ignore[no-untyped-def]
            changed = []
            flipped = False
            for name, content in payload:
                if not flipped and name != "bundle/MANIFEST.json" and content:
                    content = bytes([content[0] ^ 1]) + content[1:]
                    flipped = True
                changed.append((name, content))
            return changed

        mutations.append((
            "G4-X1", "bundle content tampering", flip_first_payload,
            "validator refuses a payload whose bytes no longer match the manifest",
        ))
        required_suffix = f"docs/checkpoints/{SUBJECT}/STATE.json"
        mutations.append((
            "G4-X2",
            "required evidence removal",
            lambda payload: [(name, content) for name, content in payload
                             if not name.endswith(required_suffix)],
            "validator refuses a bundle missing a required checkpoint artifact",
        ))
        mutations.append((
            "G4-X3",
            "unsafe archive path",
            lambda payload: payload + [("../escape.txt", b"escape")],
            "validator refuses path traversal members",
        ))
        mutations.append((
            "G4-X4",
            "secret-shaped payload",
            lambda payload: payload + [("bundle/LEAK.txt", b"gh" + b"p_" + (b"a" * 32))],
            "validator refuses an unallowlisted credential-shaped value",
        ))
        mutations.append((
            "G4-X5",
            "duplicate archive member",
            lambda payload: payload + [payload[0]],
            "validator refuses duplicate member names",
        ))

        for identifier, target, mutate, expected in mutations:
            candidate = bundle_directory / f"{identifier}.zip"
            rewrite_zip(bundle, candidate, mutate)
            observed = validate(candidate)
            defended = observed.returncode != 0 and "REVIEW_BUNDLE=FAIL" in observed.stdout
            attacks.append({
                "attackId": identifier,
                "target": target,
                "mutation": target,
                "expectedDefense": expected,
                "observed": (observed.stdout + observed.stderr).strip()[-1200:],
                "result": "DEFENDED" if defended else "ESCAPED",
                "source": "independent review-bundle mutation",
            })

        verification = json.loads(arguments.verification_report.read_text(encoding="utf-8"))
        live_names = {
            "quality-recovery",
            "quality-cancellation",
            "quality-timeout",
            "sandbox-tool-result-origin",
        }
        live = {item.get("name"): item for item in verification.get("stages") or []
                if item.get("name") in live_names}
        live_ok = len(live) == len(live_names) and all(
            item.get("result") == "PASS" and item.get("exitCode") == 0 for item in live.values()
        )
        control["observations"].append({
            "name": "live adversarial stage control",
            "ok": live_ok,
            "detail": {name: item.get("result") for name, item in live.items()},
        })
        attacks.append({
            "attackId": "G4-X6",
            "target": "live restart, cancellation, timeout and forged-origin boundaries",
            "mutation": "execute the four live adverse scenarios against the real stack",
            "expectedDefense": "all scenarios terminate with their fail-closed invariant preserved",
            "observed": {name: item.get("result") for name, item in live.items()},
            "result": "DEFENDED" if live_ok else "ESCAPED",
            "source": "clean-clone full verification",
        })
        secret_probe = json.loads(arguments.secret_probe.read_text(encoding="utf-8"))
        secret_observed = secret_probe.get("observed") or {}
        secret_defended = secret_probe.get("result") == "PASS"
        attacks.append({
            "attackId": "G4-X7",
            "target": "pre-persistence containment of detected credential-shaped quality output",
            "mutation": (
                "inject a synthetic GitHub-token-shaped marker into the exact record_execution "
                "redaction and evidence-store path without logging the marker"
            ),
            "expectedDefense": (
                "a value detected by the canonical secret scanner is redacted or quarantined "
                "before the durable evidence object is committed"
            ),
            "observed": {
                "scannerDetected": secret_observed.get("scannerDetected"),
                "redactionRemovedMarker": secret_observed.get("redactionRemovedMarker"),
                "persistenceAccepted": secret_observed.get("persistenceAccepted"),
                "storedContentContainsMarker": secret_observed.get("storedContentContainsMarker"),
                "storedEvidenceResolved": secret_observed.get("storedEvidenceResolved"),
            },
            "result": "DEFENDED" if secret_defended else "ESCAPED",
            "source": "independent delivered-image secret evidence probe",
        })
        control["result"] = (
            "VALID"
            if canonical_ok and all(item.get("ok") for item in control["observations"])
            else "INVALID"
        )
    except Exception as error:
        control["error"] = str(error)
    finally:
        env_copy = clone / "infra" / "compose" / ".env"
        if env_copy.is_file():
            env_copy.unlink()
        shutil.rmtree(scratch, ignore_errors=True)

    escaped = [item for item in attacks if item.get("result") != "DEFENDED"]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-INDEPENDENT-RED-TEAM",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": SUBJECT,
        "subjectCommit": EXPECTED_COMMIT,
        "generatedAt": utc_now(),
        "independence": (
            "Fresh-session audit of the sealed published subject. Independent of the implementing "
            "run, not cross-tool independent."
        ),
        "baselineControl": control,
        "attacks": attacks,
        "defended": len(attacks) - len(escaped),
        "total": len(attacks),
        "escaped": [item.get("attackId") for item in escaped],
        "result": "RED_TEAM_PASS" if control.get("result") == "VALID" and not escaped
                  else "RED_TEAM_FAIL",
    }
    output = arguments.report.resolve()
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"INDEPENDENT_RED_TEAM={report['result']} defended={report['defended']}/{report['total']} "
        f"control={control.get('result')}"
    )
    for item in attacks:
        print(f"- {item.get('attackId')}: {item.get('result')} — {item.get('target')}")
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
