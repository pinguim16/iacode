"""Real Git bytes for declared observations; archive/checkout modes are not cross-tool proof."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/development-ledger"))
from ledger_common import resolve_latest

ROOT = Path(__file__).resolve().parents[1]


def observation_paths():
    checkpoint = resolve_latest(ROOT)
    current = checkpoint.relative_to(ROOT).as_posix() + "/"
    files = json.loads((checkpoint / "FILES.json").read_bytes())
    names = []
    for group in ("filesCreated", "filesModified"):
        for row in files[group]:
            name = row["path"]
            inherited = (
                name.startswith("docs/checkpoints/") and not name.startswith(current)
            ) or name.startswith("docs/audits/")
            owned_observation = name.startswith(current) and (
                name.endswith((".log", ".raw", ".stdout.json", ".stderr.json"))
                or any(part.endswith("attempts") for part in Path(name).parts)
            )
            if inherited or owned_observation:
                path = ROOT / name
                if path.is_symlink() or path.is_junction() or not path.is_file():
                    raise ValueError(
                        "Declared copied observation must remain a regular actual file"
                    )
                names.append(name)
    return sorted(set(names))


class M2ObservationTransportTests(unittest.TestCase):
    def command(self, root, arguments):
        result = subprocess.run(
            ["git", *arguments], cwd=root, capture_output=True, timeout=120, check=False
        )
        self.assertEqual(0, result.returncode, "actual isolated Git operation failed")
        return result.stdout

    def transport(self, attributes, payloads):
        observations = []
        with tempfile.TemporaryDirectory(prefix="iacode-m2-observation-git-") as temporary:
            owner = Path(temporary)
            source = owner / "source"
            source.mkdir()
            (source / ".gitattributes").write_bytes(attributes)
            for name, raw in payloads.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            self.command(source, ["init", "-b", "main"])
            self.command(
                source, ["-c", "core.autocrlf=true", "-c", "core.safecrlf=false", "add", "-A"]
            )
            self.command(
                source,
                [
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-m",
                    "exact copied observation fixture",
                ],
            )
            archive = self.command(source, ["archive", "--format=tar", "HEAD"])
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
                for name, expected in payloads.items():
                    stored = bundle.extractfile(name).read()
                    observations.append(("git-archive", name, stored == expected))
            for mode in ("false", "true"):
                clone = owner / ("checkout-" + mode)
                self.command(
                    owner,
                    ["-c", "core.autocrlf=" + mode, "clone", "--no-local", str(source), str(clone)],
                )
                for name, expected in payloads.items():
                    stored = (clone / name).read_bytes()
                    observations.append(("checkout-autocrlf-" + mode, name, stored == expected))
        self.assertFalse(owner.exists(), "actual Git fixture and copies must be removed")
        return observations

    def test_every_declared_copied_observation_survives_actual_archive_and_both_checkout_modes(
        self,
    ):
        names = observation_paths()
        self.assertTrue(names, "canonical declared observations, not a caller-selected empty set")
        payloads = {name: (ROOT / name).read_bytes() for name in names}
        facts = self.transport((ROOT / ".gitattributes").read_bytes(), payloads)
        mismatches = [(mode, name) for mode, name, matched in facts if not matched]
        self.assertEqual(
            [], mismatches, "copied originals changed; never normalize them to match the transport"
        )

    def test_removing_byte_boundaries_is_detected_beside_actual_binary_null(self):
        checkpoint = resolve_latest(ROOT).relative_to(ROOT).as_posix()
        family = checkpoint + "/quality-attempts/transport-control/"
        payloads = {
            family + "stdout.log": b"LF_ORIGINAL\n",
            family + "stderr.log": b"CRLF_ORIGINAL\r\n",
            family + "binary-null.raw": b"\0BINARY_NULL\r\n",
        }
        original = (ROOT / ".gitattributes").read_bytes()
        weakened = (
            b"\n".join(line for line in original.splitlines() if b"-text" not in line) + b"\n"
        )
        facts = self.transport(weakened, payloads)
        nulls = [matched for _mode, name, matched in facts if name.endswith("binary-null.raw")]
        self.assertEqual(
            [True, True, True], nulls, "the actual no-normalization binary null must be valid"
        )
        self.assertTrue(any(not matched for _mode, name, matched in facts if name.endswith(".log")))
        protected = self.transport(original, payloads)
        self.assertTrue(all(matched for _mode, _name, matched in protected))

    def test_next_checkpoint_and_other_gate_observations_keep_the_same_real_byte_boundaries(self):
        # A repair for only the current checkpoint must not strand its fresh auditor.
        # These are isolated Git fixture paths, never new repository checkpoints or Gates.
        families = (
            "continuation-attempts",
            "attempts",
            "controls",
            "causal-attempts",
            "environment-attempts",
            "quality-attempts",
            "byte-transport-attempts",
            "raw-preimages",
            "resource-observations/build-history",
            "history-diagnostics",
            "published-green-keeper",
            "full-verifier-executions",
            "suite-attempts",
        )
        payloads = {}
        for checkpoint in ("GATE-7-CP-0004", "GATE-6-CP-9999"):
            for family in families:
                prefix = "docs/checkpoints/" + checkpoint + "/" + family + "/future-control/"
                payloads.update(
                    {
                        prefix + "stdout.log": b"LF_ORIGINAL\n",
                        prefix + "stderr.log": b"CRLF_ORIGINAL\r\n",
                        prefix + "binary-null.raw": b"\0BINARY_NULL\r\n",
                    }
                )
        facts = self.transport((ROOT / ".gitattributes").read_bytes(), payloads)
        nulls = [matched for _mode, name, matched in facts if name.endswith("binary-null.raw")]
        self.assertTrue(nulls and all(nulls), "all actual binary nulls must remain valid")
        self.assertEqual(
            [],
            [(mode, name) for mode, name, matched in facts if not matched],
            "observation-byte protection must follow the canonical family, not one delivery ID",
        )


if __name__ == "__main__":
    unittest.main()
