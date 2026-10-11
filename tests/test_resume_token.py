"""
Unit tests for Resume Token generation and verification.
"""
import unittest
import tempfile
from agent_blackbox.recorder import FlightRecorder
from agent_blackbox.resume_token import generate_resume_token, unpack_resume_token

class TestResumeToken(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.recorder = FlightRecorder(storage_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_events_token(self):
        res = generate_resume_token([])
        self.assertEqual(res["confirmed_count"], 0)
        self.assertIn("No active flight telemetry", res["prompt_block"])

    def test_populated_resume_token(self):
        self.recorder.record_hypothesis(goal="Fix database deadlock", hypothesis="Add row-level lock", confidence=0.85)
        self.recorder.record_mutation(files_changed=["src/db.py"], diff_summary="+SELECT ... FOR UPDATE")
        self.recorder.record_verification(command="pytest tests/test_db.py", exit_code=1, summary="Deadlock detected", passed=False)
        self.recorder.record_decision(status="REVERTED", rationale="Row-level lock causes lock escalation in Postgres")

        self.recorder.record_hypothesis(goal="Fix database deadlock", hypothesis="Use advisory locks", confidence=0.90)
        self.recorder.record_decision(status="CONFIRMED", rationale="Advisory locks eliminate table escalation")

        events = self.recorder.get_events()
        token_data = generate_resume_token(events)

        prompt = token_data["prompt_block"]
        self.assertIn("Goal: Fix database deadlock", prompt)
        self.assertIn("Locked In Decisions:", prompt)
        self.assertIn("Advisory locks eliminate table escalation", prompt)
        self.assertIn("Abandoned / Failed Paths (DO NOT REPEAT):", prompt)
        self.assertIn("REVERTED: Row-level lock causes lock escalation", prompt)
        self.assertIn("Active Files: src/db.py", prompt)
        self.assertTrue(token_data["token"].startswith("bbx_"))

        unpacked = unpack_resume_token(token_data["token"])
        self.assertTrue(unpacked["valid"])

if __name__ == "__main__":
    unittest.main()
