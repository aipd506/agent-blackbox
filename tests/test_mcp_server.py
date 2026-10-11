"""
Unit tests for Model Context Protocol (MCP) server handler.
"""
import unittest
import tempfile
from agent_blackbox.recorder import FlightRecorder
from agent_blackbox.mcp_server import handle_mcp_request

class TestMcpServer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.recorder = FlightRecorder(storage_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialize_handshake(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        res = handle_mcp_request(req, self.recorder)
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["serverInfo"]["name"], "agent-blackbox-mcp")

    def test_tools_list(self):
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        res = handle_mcp_request(req, self.recorder)
        tools = res["result"]["tools"]
        self.assertEqual(len(tools), 6)
        tool_names = [t["name"] for t in tools]
        self.assertIn("blackbox_record_hypothesis", tool_names)
        self.assertIn("blackbox_get_resume_token", tool_names)

    def test_tools_call_record_and_resume(self):
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "blackbox_record_hypothesis",
                "arguments": {"goal": "Speed up search", "hypothesis": "Add BM25 index"}
            }
        }
        res = handle_mcp_request(call_req, self.recorder)
        self.assertIn("Recorded hypothesis", res["result"]["content"][0]["text"])

        resume_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "blackbox_get_resume_token", "arguments": {}}
        }
        resume_res = handle_mcp_request(resume_req, self.recorder)
        token_text = resume_res["result"]["content"][0]["text"]
        self.assertIn("Goal: Speed up search", token_text)

if __name__ == "__main__":
    unittest.main()
