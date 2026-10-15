from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from secret_scan import component_digest, scan_text


class PublicationTransportScanningTests(unittest.TestCase):
    def test_publication_scan_rejects_nested_json_in_mixed_logs(self) -> None:
        marker = "gh" + "p_" + "u" * 20
        transport = json.dumps(json.dumps({"ordinary": "\n" + marker}))
        found = scan_text("ordinary log\n" + transport + "\nshutdown")
        self.assertTrue(any(kind == "GitHub credential" and not allowed
                            for kind, _line, allowed in found))

    def test_raw_allowlist_cannot_mask_another_encoded_value_of_the_same_kind(self) -> None:
        reviewed = "gh" + "p_" + "v" * 20
        prohibited = "gh" + "p_" + "w" * 20
        allowed = frozenset({
            ("GitHub credential", component_digest("GitHub credential", reviewed)),
        })
        found = scan_text(reviewed + "\n" + json.dumps({"ordinary": "\n" + prohibited}), allowed)
        self.assertTrue(any(item[2] for item in found))
        self.assertTrue(any(not item[2] for item in found))

    def test_reviewed_url_component_remains_allowed_after_json_transport(self) -> None:
        url = "postgresql://iacode:" + "reviewed-fixture-only" + "@db/iacode"
        allowed = frozenset({
            ("URL with credentials", component_digest("URL with credentials", url)),
        })
        found = scan_text(json.dumps({"ordinary": url}), allowed)
        self.assertTrue(found)
        self.assertTrue(all(item[2] for item in found))

    def test_clean_mixed_transport_stays_usable(self) -> None:
        self.assertEqual(scan_text('ordinary log\n{"output":"clean"}\nshutdown'), [])

    def test_encoded_allowlist_matches_only_the_reviewed_component(self) -> None:
        reviewed = "Bearer " + "abcdefghijklmnop"
        allowed = frozenset({
            ("bearer credential", component_digest("bearer credential", reviewed)),
        })
        encoded = json.dumps(json.dumps({"ordinary": "\n" + reviewed}))
        found = scan_text("ordinary prefix " + encoded, allowed)
        self.assertTrue(found)
        self.assertTrue(all(item[2] for item in found))
        other = json.dumps({"ordinary": "\nBearer " + "qrstuvwxyzabcdef"})
        self.assertTrue(any(not item[2] for item in scan_text(other, allowed)))
