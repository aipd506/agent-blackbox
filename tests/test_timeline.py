"""
Unit tests for Timeline rendering module.
"""
import unittest
import tempfile
from agent_blackbox.recorder import FlightRecorder
from agent_blackbox.timeline import render_timeline

class TestTimeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.recorder = FlightRecorder(storage_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_timeline_rendering(self):
        self.recorder.record_hypothesis(goal="Optimize cache", hypothesis="Use LRU eviction")
        self.recorder.record_decision(status="CONFIRMED", rationale="LRU reduces cache thrashing by 80%")

        events = self.recorder.get_events()
        timeline = render_timeline(events)

        self.assertIn("AGENT-BLACKBOX FLIGHT DATA TIMELINE", timeline)
        self.assertIn("[HYPOTHESIS]", timeline)
        self.assertIn("[DECISION] >>> CONFIRMED <<<", timeline)
        self.assertIn("LRU reduces cache thrashing by 80%", timeline)

if __name__ == "__main__":
    unittest.main()
