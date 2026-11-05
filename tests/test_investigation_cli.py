import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from logsentry.cli import main

class InvestigationCLITests(unittest.TestCase):
    def test_investigate_json_output(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "events.json"
            file.write_text(json.dumps([{"event_id":4625,"timestamp":f"2026-01-01T00:0{i}:00Z"} for i in range(5)]), encoding="utf-8")
            output = StringIO()
            with patch("sys.argv",["logsentry",str(file),"--investigate","--format","json"]),patch("sys.stdout",output):
                self.assertEqual(main(),0)
            report=json.loads(output.getvalue())
            self.assertEqual(report["investigation"]["findings"][0]["type"],"authentication_failure_burst")
    def test_investigate_text_output(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "events.json"
            file.write_text('[{"event_id":4740,"timestamp":"2026-01-01T00:00:00Z"}]',encoding="utf-8")
            output=StringIO()
            with patch("sys.argv",["logsentry",str(file),"--investigate"]),patch("sys.stdout",output):
                self.assertEqual(main(),0)
            self.assertIn("account_lockouts",output.getvalue())

if __name__=="__main__":
    unittest.main()
