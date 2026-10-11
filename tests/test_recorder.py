"""
Unit tests for FlightRecorder engine.
"""
import os
import unittest
import tempfile
from agent_blackbox.recorder import FlightRecorder
from agent_blackbox.models import FlightEventType

class TestRecorder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_record_all_event_types(self):
        recorder = FlightRecorder(storage_dir=self.temp_dir.name)

        e1 = recorder.record_hypothesis(goal="Implement auth", hypothesis="Use JWT rotation", confidence=0.9)
        self.assertEqual(e1.event_type, FlightEventType.HYPOTHESIS)
        self.assertEqual(e1.data["goal"], "Implement auth")

        e2 = recorder.record_mutation(files_changed=["src/auth.py"], diff_summary="+def refresh():", lines_added=5, lines_deleted=1)
        self.assertEqual(e2.event_type, FlightEventType.MUTATION)
        self.assertEqual(e2.data["files_changed"], ["src/auth.py"])

        e3 = recorder.record_verification(command="pytest", exit_code=0, summary="10 passed", passed=True)
        self.assertEqual(e3.event_type, FlightEventType.VERIFICATION)
        self.assertTrue(e3.data["passed"])

        e4 = recorder.record_decision(status="CONFIRMED", rationale="Tests verify token rotation works")
        self.assertEqual(e4.event_type, FlightEventType.DECISION)
        self.assertEqual(e4.data["status"], "CONFIRMED")

        # Reload from disk
        events = recorder.get_events()
        self.assertEqual(len(events), 4)
        self.assertEqual(events[0].event_id, e1.event_id)
        self.assertEqual(events[3].data["status"], "CONFIRMED")

if __name__ == "__main__":
    unittest.main()
