"""CLI report-export tests."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliOutputTests(unittest.TestCase):
    def test_json_report_can_be_written_to_a_file(self):
        root = Path(__file__).resolve().parents[1]
        sample = root / "samples" / "security-events.json"
        if not sample.exists():
            self.skipTest("documented sample fixture is not present")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            result = subprocess.run(
                [sys.executable, "-m", "logsentry", str(sample), "--format", "json", "--output", str(output)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("total_events", report)


if __name__ == "__main__":
    unittest.main()
