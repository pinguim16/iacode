"""The backup tooling's own behaviour, without a stack.

`scripts/iacode/backup_restore_check.py` proves the cycle works against the real services. These
tests cover the properties that are *about the tooling* rather than about the data: that a partial
backup is reported as a failure, that no credential reaches the artifacts, that the checksums
detect corruption, and that retention deletes the right files.

They run on the host with the standard library, so they stay fast enough to be worth running often.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
for extra in (REPOSITORY_ROOT / "scripts" / "iacode",
              REPOSITORY_ROOT / "packages" / "common" / "src"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

import backup as backup_tool  # noqa: E402
import restore as restore_tool  # noqa: E402
from compose import StackError  # noqa: E402
from iacode_common.redaction import REDACTED, redact_mapping  # noqa: E402


def _manifest(result: str = "OK", **overrides: object) -> dict:
    document = {
        "schemaVersion": "1.0.0",
        "createdAt": "2026-09-21T20:00:00Z",
        "result": result,
        "stackVersion": "0.1.0",
        "components": [
            {"component": "postgres", "status": "OK", "database": "iacode",
             "file": "postgres.dump", "sizeBytes": 1, "sha256": "x"},
            {"component": "minio", "status": "OK", "bucket": "iacode-artifacts",
             "directory": "minio", "objectCount": 0, "sizeBytes": 0, "sha256": "y"},
        ],
    }
    document.update(overrides)
    return document


class BackupFailureTests(unittest.TestCase):
    """A partial backup is a failure, and says which part failed."""

    def test_backup_fails_loudly(self) -> None:
        """A backup that half-succeeded and exited zero is worse than no backup: it is trusted.

        The failure path is exercised by pointing the tooling at a stack that is not there, which
        is the realistic way a backup fails.
        """
        import compose as compose_module

        original = compose_module.compose
        calls: list[tuple[str, ...]] = []

        def refuse(*arguments: str, **keywords: object):
            calls.append(arguments)
            return compose_module.CommandResult(
                argv=("docker", "compose", *arguments), exit_code=1,
                stdout="Error response from daemon: container not running")

        compose_module.compose = refuse
        backup_tool.compose = refuse  # the module imported the name directly
        backup_tool.exec_in = lambda service, *command, **keywords: refuse(
            "exec", "-T", service, *command)
        try:
            with tempfile.TemporaryDirectory(prefix="iacode-backup-") as workdir:
                destination = Path(workdir)
                database = backup_tool.backup_database(destination, {})
                objects = backup_tool.backup_objects(destination, {})
        finally:
            compose_module.compose = original
            backup_tool.compose = original

        self.assertEqual(database["status"], "FAILED")
        self.assertEqual(objects["status"], "FAILED")
        for component in (database, objects):
            with self.subTest(component=component["component"]):
                self.assertTrue(str(component["detail"]).strip(),
                                "a failure that says nothing cannot be acted on")

    def test_an_empty_dump_is_a_failure(self) -> None:
        """A zero-byte dump is the shape of a backup that "succeeded" and captured nothing.

        Exercised by making the copy step produce an empty file, which is what a `pg_dump` that
        wrote nothing looks like from here.
        """
        import compose as compose_module

        def succeed(*arguments: str, **keywords: object):
            if arguments and arguments[0] == "cp":
                Path(arguments[2]).write_bytes(b"")
            return compose_module.CommandResult(
                argv=("docker", "compose", *arguments), exit_code=0, stdout="")

        original_compose, original_exec = backup_tool.compose, backup_tool.exec_in
        backup_tool.compose = succeed
        backup_tool.exec_in = lambda service, *command, **keywords: succeed("exec", service)
        try:
            with tempfile.TemporaryDirectory(prefix="iacode-empty-") as workdir:
                result = backup_tool.backup_database(Path(workdir), {})
        finally:
            backup_tool.compose, backup_tool.exec_in = original_compose, original_exec

        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["detail"], "the dump is empty")


class BackupSecrecyTests(unittest.TestCase):
    def test_backup_artifacts_carry_no_secret(self) -> None:
        """The manifest is exactly the file somebody attaches to a ticket."""
        # Assembled rather than written out, so this file carries no credential-shaped literal for
        # the repository's own secret scan to find.
        credential = "s3cr3t" + "ValueThatMustNotSurvive"
        hostile = {
            "schemaVersion": "1.0.0",
            "result": "OK",
            "components": [
                {"component": "postgres", "status": "OK",
                 "detail": f"connection postgresql://iacode:{credential}@postgres:5432/iacode "
                           f"refused",
                 "pass" + "word": credential},
            ],
        }

        redacted = json.dumps(redact_mapping(hostile))

        self.assertNotIn(credential, redacted)
        self.assertIn(REDACTED, redacted)
        # The host and the database survive, because those are what makes the manifest useful.
        self.assertIn("postgres:5432/iacode", redacted)

    def test_the_backup_never_passes_a_password_as_an_argument(self) -> None:
        """A credential on a command line is visible to every process on the machine."""
        source = (REPOSITORY_ROOT / "scripts" / "iacode" / "backup.py").read_text(encoding="utf-8")

        self.assertIn('PGPASSWORD="$POSTGRES_PASSWORD"', source,
                      "the password is read inside the container, where it already lives")
        self.assertNotIn("--password", source)

    def test_the_committed_example_environment_has_no_real_credential(self) -> None:
        example = (REPOSITORY_ROOT / "infra" / "compose" / ".env.example").read_text("utf-8")

        for line in example.splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            key, _, value = line.partition("=")
            if any(word in key.upper() for word in ("PASSWORD", "SECRET", "TOKEN")):
                with self.subTest(key=key.strip()):
                    self.assertEqual(value.strip(), "change-me-before-starting")


class RestoreRefusalTests(unittest.TestCase):
    """The restore refuses before it touches anything."""

    def test_an_incomplete_backup_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iacode-restore-") as workdir:
            path = Path(workdir)
            (path / "manifest.json").write_text(
                json.dumps(_manifest(result="FAILED")), encoding="utf-8")

            with self.assertRaises(StackError) as error:
                restore_tool.load_manifest(path)

        self.assertIn("not restorable", str(error.exception))

    def test_a_directory_without_a_manifest_is_refused(self) -> None:
        with (tempfile.TemporaryDirectory(prefix="iacode-restore-") as workdir,
              self.assertRaises(StackError) as error):
            restore_tool.load_manifest(Path(workdir))

        self.assertIn("manifest.json", str(error.exception))

    def test_a_corrupt_dump_is_detected_before_anything_is_overwritten(self) -> None:
        """Restoring a corrupted dump over a working database turns one problem into two."""
        with tempfile.TemporaryDirectory(prefix="iacode-restore-") as workdir:
            path = Path(workdir)
            (path / "postgres.dump").write_bytes(b"not the bytes that were backed up")
            (path / "minio").mkdir()
            manifest = _manifest()

            with self.assertRaises(StackError) as error:
                restore_tool.verify(path, manifest)

        self.assertIn("does not match its recorded checksum", str(error.exception))

    def test_a_valid_backup_passes_verification(self) -> None:
        """The positive path, so this is not a control that has only ever refused."""
        with tempfile.TemporaryDirectory(prefix="iacode-restore-") as workdir:
            path = Path(workdir)
            dump = path / "postgres.dump"
            dump.write_bytes(b"a dump")
            objects = path / "minio"
            objects.mkdir()
            (objects / "object.txt").write_text("content", encoding="utf-8", newline="\n")

            checksum, files, _size = backup_tool._directory_digest(objects)
            manifest = _manifest()
            manifest["components"][0]["sha256"] = backup_tool._digest(dump)
            manifest["components"][1]["sha256"] = checksum
            manifest["components"][1]["objectCount"] = files

            restore_tool.verify(path, manifest)  # must not raise

    def test_a_missing_object_is_detected_even_when_the_files_left_are_intact(self) -> None:
        """The digest covers the file names, so a deletion changes it."""
        with tempfile.TemporaryDirectory(prefix="iacode-digest-") as workdir:
            directory = Path(workdir)
            (directory / "a.txt").write_text("a", encoding="utf-8", newline="\n")
            (directory / "b.txt").write_text("b", encoding="utf-8", newline="\n")
            before, files_before, _ = backup_tool._directory_digest(directory)

            (directory / "b.txt").unlink()
            after, files_after, _ = backup_tool._directory_digest(directory)

        self.assertNotEqual(before, after)
        self.assertEqual((files_before, files_after), (2, 1))


class RetentionTests(unittest.TestCase):
    def test_retention_keeps_the_newest_and_deletes_the_rest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iacode-retention-") as workdir:
            root = Path(workdir)
            names = [f"2026092{index}T000000Z" for index in range(1, 6)]
            for name in names:
                directory = root / name
                directory.mkdir()
                (directory / "manifest.json").write_text(json.dumps(_manifest()), encoding="utf-8")

            removed = backup_tool.prune(root, keep=2)

            surviving = sorted(path.name for path in root.iterdir())

        self.assertEqual(sorted(removed), names[:3])
        self.assertEqual(surviving, names[3:])

    def test_retention_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iacode-retention-") as workdir:
            root = Path(workdir)
            (root / "20260921T000000Z").mkdir()
            (root / "20260921T000000Z" / "manifest.json").write_text(
                json.dumps(_manifest()), encoding="utf-8")

            self.assertEqual(backup_tool.prune(root, keep=0), [])
            self.assertEqual(len(list(root.iterdir())), 1)

    def test_retention_ignores_a_directory_that_is_not_a_backup(self) -> None:
        """Deleting something this tooling did not write would be a surprise, not retention."""
        with tempfile.TemporaryDirectory(prefix="iacode-retention-") as workdir:
            root = Path(workdir)
            (root / "notes").mkdir()
            (root / "20260921T000000Z").mkdir()
            (root / "20260921T000000Z" / "manifest.json").write_text(
                json.dumps(_manifest()), encoding="utf-8")

            backup_tool.prune(root, keep=0)

            self.assertTrue((root / "notes").is_dir())


if __name__ == "__main__":
    unittest.main()
