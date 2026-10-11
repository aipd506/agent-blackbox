"""
Unit tests for Agent-Blackbox CLI execution.
"""
import io
import os
import unittest
from unittest.mock import patch
import tempfile
from agent_blackbox.cli import main

class TestCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.bbx_dir = os.path.join(self.temp_dir.name, ".blackbox")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_version_flag(self):
        with io.StringIO() as buf, patch("sys.stdout", buf):
            with self.assertRaises(SystemExit) as cm:
                main(["--version"])
            self.assertEqual(cm.exception.code, 0)

    def test_cli_lifecycle_end_to_end(self):
        # 1. init
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "init"])
            self.assertEqual(ret, 0)

        # 2. hypothesis
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "hypothesis", "--goal", "Fix bug", "--text", "Check null pointer"])
            self.assertEqual(ret, 0)

        # 3. mutation
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "mutation", "--files", "src/main.py,src/utils.py", "--added", "10", "--deleted", "2"])
            self.assertEqual(ret, 0)

        # 4. verify
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "verify", "--command", "pytest", "--exit-code", "0", "--passed", "--summary", "10 passed"])
            self.assertEqual(ret, 0)

        # 5. decision
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "decision", "--status", "CONFIRMED", "--rationale", "Bug solved"])
            self.assertEqual(ret, 0)

        # 6. timeline
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "timeline"])
            self.assertEqual(ret, 0)
            self.assertIn("AGENT-BLACKBOX FLIGHT DATA TIMELINE", buf.getvalue())

        # 7. resume
        with io.StringIO() as buf, patch("sys.stdout", buf):
            ret = main(["--dir", self.bbx_dir, "resume"])
            self.assertEqual(ret, 0)
            self.assertIn("Goal: Fix bug", buf.getvalue())
            self.assertIn("Bug solved", buf.getvalue())

if __name__ == "__main__":
    unittest.main()
