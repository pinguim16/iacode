"""The development Git policy of `ADR-0024`: a public remote, a scanned history, a checked sync.

Every credential planted here is assembled at run time. A literal would be a credential-shaped value
in a public history, which is the exact thing the scanner under test exists to refuse.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "development-ledger"))

import remote_sync  # noqa: E402
import secret_scan  # noqa: E402

PLANTED_TOKEN = "ghp_" + "Q7" * 18
PLANTED_KEY = "sk-" + "live" + "Xy9" * 6


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True,
                               text=True)
    return completed.stdout.strip()


def init_repository(root: Path) -> None:
    (root / ".iacode" / "policies").mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")


def commit_file(root: Path, name: str, content: str, message: str = "change") -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    git(root, "add", name)
    git(root, "commit", "-q", "-m", message)


def scan(root: Path, *mode: str) -> tuple[int, str]:
    output = io.StringIO()
    errors = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        code = secret_scan.main([*mode, "--root", str(root)])
    return code, output.getvalue() + errors.getvalue()


class SecretScanTests(unittest.TestCase):
    """The history scan finds what a later commit removed, and never repeats what it found."""

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="iacode-scan-")
        self.root = Path(self._directory.name)
        init_repository(self.root)
        commit_file(self.root, "README.md", "a clean project\n", "start")

    def tearDown(self) -> None:
        self._directory.cleanup()

    def test_a_clean_history_passes(self) -> None:
        """The null control: the identical scan accepts a history with nothing in it."""
        code, report = scan(self.root, "--history")
        self.assertEqual(code, 0, report)
        self.assertIn("SECRET_SCAN_CLEAN", report)

    def test_the_history_scan_finds_a_secret_a_later_commit_removed(self) -> None:
        commit_file(self.root, "config.txt", f"token {PLANTED_TOKEN}\n", "plant")
        commit_file(self.root, "config.txt", "token removed\n", "remove")

        tree_code, _ = scan(self.root, "--tree")
        history_code, report = scan(self.root, "--history")

        self.assertEqual(tree_code, 0, "the tip no longer carries it, which is the whole trap")
        self.assertEqual(history_code, 1, report)
        self.assertIn("path=config.txt", report)
        self.assertIn("GitHub credential", report)

    def test_a_finding_never_prints_the_value(self) -> None:
        commit_file(self.root, "keys.env.txt", f"KEY {PLANTED_KEY}\nT {PLANTED_TOKEN}\n")
        for mode in ("--history", "--tree"):
            for extra in ((), ("--json",)):
                with self.subTest(mode=mode, json=bool(extra)):
                    code, report = scan(self.root, mode, *extra)
                    self.assertEqual(code, 1)
                    self.assertNotIn(PLANTED_KEY, report)
                    self.assertNotIn(PLANTED_TOKEN, report)
                    self.assertNotIn(PLANTED_TOKEN[4:], report)

    def test_a_commit_message_is_scanned(self) -> None:
        commit_file(self.root, "notes.txt", "notes\n", f"deploy with {PLANTED_TOKEN}")
        code, report = scan(self.root, "--history")
        self.assertEqual(code, 1, report)
        self.assertIn("location=commit-message", report)

    def test_a_url_carrying_a_password_is_found(self) -> None:
        url = "postgresql://svc:" + "Pw7" * 4 + "@db.internal:5432/app"
        commit_file(self.root, "settings.txt", f"url = {url}\n")
        code, report = scan(self.root, "--history")
        self.assertEqual(code, 1, report)
        self.assertIn("URL with credentials", report)

    def test_the_staged_scan_judges_only_the_staged_content(self) -> None:
        (self.root / "staged.txt").write_text(f"t {PLANTED_TOKEN}\n", encoding="utf-8")
        (self.root / "unstaged.txt").write_text("clean\n", encoding="utf-8")
        clean_code, _ = scan(self.root, "--staged")
        git(self.root, "add", "staged.txt")
        dirty_code, report = scan(self.root, "--staged")

        self.assertEqual(clean_code, 0)
        self.assertEqual(dirty_code, 1, report)
        self.assertIn("path=staged.txt", report)

    def test_the_allowlist_matches_the_value_and_not_the_path(self) -> None:
        digest = hashlib.sha256(PLANTED_TOKEN.encode("utf-8")).hexdigest()
        (self.root / ".iacode" / "policies" / "secret-scan-allowlist.json").write_text(
            json.dumps({"schemaVersion": "1.0.0", "policy": "fixture", "entries": [
                {"kind": "GitHub credential", "sha256": digest, "reason": "fixture value"}]}),
            encoding="utf-8")
        commit_file(self.root, "a.txt", f"t {PLANTED_TOKEN}\n")
        allowed_code, allowed_report = scan(self.root, "--history")
        commit_file(self.root, "a.txt", f"t {PLANTED_TOKEN}\nk {PLANTED_KEY}\n")
        mixed_code, mixed_report = scan(self.root, "--history")

        self.assertEqual(allowed_code, 0, allowed_report)
        self.assertIn("allowlisted=", allowed_report)
        self.assertNotIn("allowlisted=0", allowed_report, "an allowed value is still counted")
        self.assertEqual(mixed_code, 1, "a real key in an allowed file is still a finding")
        self.assertIn("OpenAI-style key", mixed_report)

    def test_a_malformed_allowlist_stops_the_scan(self) -> None:
        (self.root / ".iacode" / "policies" / "secret-scan-allowlist.json").write_text(
            json.dumps({"entries": [{"kind": "GitHub credential", "sha256": "abc"}]}),
            encoding="utf-8")
        code, report = scan(self.root, "--history")
        self.assertEqual(code, 2, report)
        self.assertIn("SECRET_SCAN_ERROR", report)

    def test_every_allowlist_entry_names_a_known_kind_and_a_reason(self) -> None:
        allowed = secret_scan.load_allowlist(PROJECT_ROOT)
        self.assertTrue(allowed, "the repository's reviewed allowlist is empty or missing")
        kinds = {name for name, _pattern in secret_scan.ALL_PATTERNS}
        self.assertTrue({kind for kind, _digest in allowed} <= kinds)


class PublishedHistoryTests(unittest.TestCase):
    """The repository's own history, which is public, carries no credential."""

    def test_the_published_history_carries_no_credential(self) -> None:
        code, report = scan(PROJECT_ROOT, "--history")
        self.assertEqual(code, 0, report[-2000:])


class RemoteSyncTests(unittest.TestCase):
    """`remote_sync.py` asks the remote, and a claim of synchronisation is only made when true."""

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="iacode-sync-")
        base = Path(self._directory.name)
        self.remote = base / "remote.git"
        git(base, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.root = base / "work"
        self.root.mkdir()
        init_repository(self.root)
        commit_file(self.root, "README.md", "work\n", "start")
        self.url = str(self.remote)
        git(self.root, "remote", "add", "origin", self.url)
        git(self.root, "tag", "iacode-checkpoints/FIXTURE-CP-0001")
        git(self.root, "push", "-q", "origin", "main",
            "refs/tags/iacode-checkpoints/FIXTURE-CP-0001")

    def tearDown(self) -> None:
        self._directory.cleanup()

    def sync(self, *extra: str) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = remote_sync.main(["--root", str(self.root), "--authorised-url", self.url,
                                     *extra])
        return code, output.getvalue()

    def test_a_synchronised_branch_and_tag_pass(self) -> None:
        """The null control: the identical check accepts a remote that has everything."""
        code, report = self.sync("--tag", "iacode-checkpoints/FIXTURE-CP-0001")
        self.assertEqual(code, 0, report)
        self.assertIn("REMOTE_SYNC_PASS", report)

    def test_an_unpushed_commit_fails(self) -> None:
        commit_file(self.root, "more.txt", "more\n", "local only")
        code, report = self.sync()
        self.assertEqual(code, 1, report)
        self.assertIn("NOT_SYNCHRONISED", report)

    def test_a_tag_missing_from_the_remote_fails(self) -> None:
        git(self.root, "tag", "iacode-checkpoints/FIXTURE-CP-0002")
        code, report = self.sync("--tag", "iacode-checkpoints/FIXTURE-CP-0002")
        self.assertEqual(code, 1, report)
        self.assertIn("is not on origin", report)

    def test_a_remote_other_than_the_authorised_one_fails(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = remote_sync.main(["--root", str(self.root)])
        self.assertEqual(code, 1, output.getvalue())
        self.assertIn("not the authorised", output.getvalue())

    def test_an_unreachable_remote_is_unavailable_and_never_a_pass(self) -> None:
        git(self.root, "remote", "set-url", "origin", str(self.remote) + "-absent")
        self.url = str(self.remote) + "-absent"
        code, report = self.sync()
        self.assertEqual(code, 2, report)
        self.assertIn("REMOTE_SYNC_UNAVAILABLE", report)
        self.assertNotIn("REMOTE_SYNC_PASS", report)

    def test_the_authorised_remote_is_the_one_the_policy_names(self) -> None:
        contract = (PROJECT_ROOT / "docs" / "DEVELOPMENT-CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn(remote_sync.AUTHORISED_REMOTE, contract)
        self.assertEqual(remote_sync.DEFAULT_BRANCH, "main")


class GitPolicyDocumentationTests(unittest.TestCase):
    """The policy is written where a new session reads it first, and says every rule."""

    def test_the_contract_states_every_rule_of_the_policy(self) -> None:
        contract = (PROJECT_ROOT / "docs" / "DEVELOPMENT-CONTRACT.md").read_text(encoding="utf-8")
        for phrase in ("https://github.com/pinguim16/iacode.git", "`main`",
                       "secret_scan.py --history", "secret_scan.py --staged",
                       "one logical advance", "git push origin main", "never amended",
                       "never moved or deleted", "credential store",
                       "git log origin/main..main"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, contract)

    def test_the_decision_is_recorded_as_an_adr(self) -> None:
        adr = PROJECT_ROOT / "docs" / "adr" / "ADR-0024-public-remote-and-atomic-commits.md"
        text = adr.read_text(encoding="utf-8")
        self.assertIn("ADR-0005", text, "the workflow ADR it extends is named")
        self.assertIn("force", text)


if __name__ == "__main__":
    unittest.main()
