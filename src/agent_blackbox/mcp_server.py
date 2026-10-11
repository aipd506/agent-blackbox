"""
Model Context Protocol (MCP) stdio server for Agent-Blackbox.
Exposes flight recorder capabilities to Claude Desktop, Cursor, and Antigravity.
"""
import sys
import json
from typing import Dict, Any, List
from .recorder import FlightRecorder
from .resume_token import generate_resume_token
from .timeline import render_timeline

MCP_TOOLS = [
    {
        "name": "blackbox_record_hypothesis",
        "description": "Records an agent hypothesis and target goal into the flight recorder.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "High-level objective"},
                "hypothesis": {"type": "string", "description": "Proposed implementation approach"},
                "confidence": {"type": "number", "description": "Confidence score 0.0 - 1.0", "default": 0.8}
            },
            "required": ["goal", "hypothesis"]
        }
    },
    {
        "name": "blackbox_record_mutation",
        "description": "Records a code diff mutation before testing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "files_changed": {"type": "array", "items": {"type": "string"}},
                "diff_summary": {"type": "string"},
                "lines_added": {"type": "integer", "default": 0},
                "lines_deleted": {"type": "integer", "default": 0}
            },
            "required": ["files_changed"]
        }
    },
    {
        "name": "blackbox_record_verification",
        "description": "Records test suite or command execution diagnostics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "exit_code": {"type": "integer"},
                "summary": {"type": "string"},
                "passed": {"type": "boolean"}
            },
            "required": ["command", "exit_code", "passed"]
        }
    },
    {
        "name": "blackbox_record_decision",
        "description": "Records an architectural decision (CONFIRMED, REVERTED, PIVOTED, ABANDONED).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["CONFIRMED", "REVERTED", "PIVOTED", "ABANDONED"]},
                "rationale": {"type": "string", "description": "Justification for decision"}
            },
            "required": ["status", "rationale"]
        }
    },
    {
        "name": "blackbox_get_resume_token",
        "description": "Retrieves the compact zero-loss resume token and prompt context block.",
        "inputSchema": {"type": "object"}
    },
    {
        "name": "blackbox_get_timeline",
        "description": "Retrieves the formatted ASCII decision tree timeline.",
        "inputSchema": {"type": "object"}
    }
]

def handle_mcp_request(req: Dict[str, Any], recorder: FlightRecorder) -> Dict[str, Any]:
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "agent-blackbox-mcp", "version": "0.1.0"}
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": MCP_TOOLS}
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "blackbox_record_hypothesis":
            evt = recorder.record_hypothesis(
                goal=args.get("goal", ""),
                hypothesis=args.get("hypothesis", ""),
                confidence=args.get("confidence", 0.8)
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": f"Recorded hypothesis {evt.event_id}"}]}
            }

        elif tool_name == "blackbox_record_mutation":
            evt = recorder.record_mutation(
                files_changed=args.get("files_changed", []),
                diff_summary=args.get("diff_summary", ""),
                lines_added=args.get("lines_added", 0),
                lines_deleted=args.get("lines_deleted", 0)
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": f"Recorded mutation {evt.event_id}"}]}
            }

        elif tool_name == "blackbox_record_verification":
            evt = recorder.record_verification(
                command=args.get("command", ""),
                exit_code=args.get("exit_code", 0),
                summary=args.get("summary", ""),
                passed=args.get("passed", False)
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": f"Recorded verification {evt.event_id}"}]}
            }

        elif tool_name == "blackbox_record_decision":
            evt = recorder.record_decision(
                status=args.get("status", "CONFIRMED"),
                rationale=args.get("rationale", "")
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": f"Recorded decision {evt.event_id} ({args.get('status')})"}]}
            }

        elif tool_name == "blackbox_get_resume_token":
            token_data = generate_resume_token(recorder.get_events())
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": token_data["prompt_block"]}]}
            }

        elif tool_name == "blackbox_get_timeline":
            timeline_str = render_timeline(recorder.get_events())
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": timeline_str}]}
            }

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method {method} not found"}
    }

def run_mcp_server():
    """Runs standard input/output JSON-RPC MCP loop."""
    recorder = FlightRecorder()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_mcp_request(req, recorder)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()
