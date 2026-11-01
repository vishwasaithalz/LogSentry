import json
import tempfile
import unittest
from pathlib import Path

from logsentry.analyzer import filter_events, parse_events, summarize


class LogSentryTests(unittest.TestCase):
    def test_parse_json_sample(self):
        events = parse_events("samples/security-events.json")
        self.assertEqual(len(events), 4)
        self.assertEqual(str(events[0]["event_id"]), "4624")

    def test_parse_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.csv"
            path.write_text("EventID,TimeCreated,Provider,Level,Message\n4625,2026-10-30T08:17:12Z,Security,Warning,Failed logon\n", encoding="utf-8")
            events = parse_events(path)
            self.assertEqual(events[0]["event_id"], "4625")
            self.assertEqual(events[0]["level"], "Warning")

    def test_parse_csv_with_quoted_multiline_message(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.csv"
            path.write_text(
                'EventID,Provider,Level,Message\n'
                '4625,Security,Warning,"Failed logon\n'
                'Additional diagnostic detail"\n',
                encoding="utf-8",
            )
            events = parse_events(path)
            self.assertEqual(len(events), 1)
            self.assertEqual(
                events[0]["message"],
                "Failed logon\nAdditional diagnostic detail",
            )

    def test_parse_wrapped_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.json"
            path.write_text(json.dumps({"Events": [{"EventID": 4625}]}), encoding="utf-8")
            self.assertEqual(len(parse_events(path)), 1)

    def test_filter_by_id_level_and_provider(self):
        events = parse_events("samples/security-events.json")
        result = filter_events(events, event_id="4625", level="warning", provider="security")
        self.assertEqual(len(result), 1)

    def test_filter_since(self):
        events = parse_events("samples/security-events.json")
        result = filter_events(events, since="2026-10-30T08:18:00Z")
        self.assertEqual(len(result), 2)

    def test_invalid_since_rejected(self):
        with self.assertRaises(ValueError):
            filter_events([], since="not-a-date")

    def test_summary_counts(self):
        report = summarize(parse_events("samples/security-events.json"))
        self.assertEqual(report["total_events"], 4)
        self.assertEqual(report["levels"]["Warning"], 2)

    def test_empty_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.json"
            path.write_text(" ", encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_events(path)


if __name__ == "__main__":
    unittest.main()
