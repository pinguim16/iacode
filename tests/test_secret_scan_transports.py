from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from secret_scan import component_digest, scan_text
from iacode_common import secret_scanning


class PublicationTransportScanningTests(unittest.TestCase):
    def test_json_error_line_index_matches_builtin_string_coordinates(self) -> None:
        text = "préface\nα\nordinary\r\nlast"
        indexed = secret_scanning._IndexedJsonText(text)
        cached = None
        for sub in ("\n", "é", "", "missing"):
            for start in (-100, -5, -1, 0, 2, 7, len(text) + 2):
                for end in (None, -100, -1, 0, 4, len(text) + 2):
                    self.assertEqual(indexed.count(sub, start, end), text.count(sub, start, end))
                    self.assertEqual(indexed.rfind(sub, start, end), text.rfind(sub, start, end))
                    if sub == "\n":
                        if cached is None:
                            cached = indexed._newlines
                        self.assertIs(indexed._newlines, cached)

    def test_indexed_decoder_errors_keep_original_messages_and_coordinates(self) -> None:
        text = 'ordinary prefix\n{"ordinary":}\n"unterminated'
        indexed = secret_scanning._IndexedJsonText(text)
        decoder = json.JSONDecoder()
        for start in (0, text.index("{"), text.rfind('"')):
            with self.assertRaises(json.JSONDecodeError) as original:
                decoder.raw_decode(text, start)
            with self.assertRaises(json.JSONDecodeError) as optimized:
                decoder.raw_decode(indexed, start)
            self.assertEqual(
                (optimized.exception.msg, optimized.exception.pos,
                 optimized.exception.lineno, optimized.exception.colno),
                (original.exception.msg, original.exception.pos,
                 original.exception.lineno, original.exception.colno),
            )

    def test_fragment_carrier_lines_count_each_source_range_at_most_once(self) -> None:
        class MeasuredText(str):
            examined_characters = 0
            caller_costs: dict[str, int] = {}

            def count(self, sub: str, start: int = 0, end: int | None = None) -> int:
                stop = len(self) if end is None else end
                work = max(0, stop - start)
                self.examined_characters += work
                caller_frame = sys._getframe(1)
                caller = Path(caller_frame.f_code.co_filename).name
                self.caller_costs[caller] = self.caller_costs.get(caller, 0) + work
                return super().count(sub, start, stop)

        marker = "gh" + "p_" + "y" * 20
        records = [json.dumps({"ordinary": "\nclean"}) for _ in range(40)]
        records.append(json.dumps({"ordinary": "\n" + marker}))
        text = MeasuredText("\n".join(records))
        found = scan_text(text)
        prohibited = [row for row in found if row[0] == "GitHub credential"]
        self.assertTrue(prohibited)
        self.assertTrue(all(row[1] == len(records) and not row[2] for row in prohibited))
        self.assertLessEqual(text.examined_characters, len(text), str(text.caller_costs))

    def test_interleaved_fragments_keep_their_distinct_carrier_lines(self) -> None:
        markers = ["gh" + "p_" + letter * 20 for letter in ("y", "z")]
        records = ["ordinary prefix", json.dumps({"ordinary": "\n" + markers[0]}),
                   "ordinary separator", json.dumps({"ordinary": "\n" + markers[1]}),
                   "ordinary shutdown"]
        found = [row for row in scan_text("\n".join(records))
                 if row[0] == "GitHub credential"]
        self.assertEqual({row[1] for row in found}, {2, 4})
        self.assertTrue(all(not row[2] for row in found))

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
