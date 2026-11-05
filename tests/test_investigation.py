import unittest
from logsentry.investigation import investigate

class InvestigationTests(unittest.TestCase):
    def test_burst_and_lockout(self):
        events=[{"event_id":4625,"timestamp":f"2026-01-01T00:0{i}:00Z"} for i in range(5)]
        events.append({"event_id":4740,"timestamp":"2026-01-01T00:06:00Z"})
        result=investigate(events)
        self.assertEqual(result["event_ids"]["4625"],5)
        self.assertEqual([x["type"] for x in result["findings"]],["authentication_failure_burst","account_lockouts"])
    def test_invalid_dates_are_skipped(self):
        result=investigate([{"event_id":"4625","timestamp":"bad"}])
        self.assertEqual(result["event_count"],1)
        self.assertFalse(result["findings"])
    def test_bad_threshold(self):
        with self.assertRaises(ValueError):
            investigate([],failure_threshold=0)

if __name__=="__main__":
    unittest.main()
