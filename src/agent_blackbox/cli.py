"""
Command-line interface for Agent-Blackbox.
"""
import sys
import os
import json
import argparse
from typing import List, Optional
from .recorder import FlightRecorder
from .resume_token import generate_resume_token
from .timeline import render_timeline
from .mcp_server import run_mcp_server
from . import __version__

def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="blackbox",
        description="The Deterministic Flight Data Recorder for Autonomous Coding Sessions."
    )
    parser.add_argument("--version", action="version", version=f"agent-blackbox {__version__}")
    parser.add_argument("--dir", type=str, default=".blackbox", help="Path to blackbox flight data directory")

    subparsers = parser.add_subparsers(dest="subcommand", help="Flight commands")

    # 1. init
    subparsers.add_parser("init", help="Initialize flight data directory in current workspace")

    # 2. hypothesis
    hypo_parser = subparsers.add_parser("hypothesis", help="Record a proposed hypothesis")
    hypo_parser.add_argument("--goal", type=str, required=True, help="Task objective")
    hypo_parser.add_argument("--text", type=str, required=True, help="Hypothesis proposal text")
    hypo_parser.add_argument("--confidence", type=float, default=0.8, help="Confidence rating (0.0-1.0)")

    # 3. mutation
    mut_parser = subparsers.add_parser("mutation", help="Record code mutation diff")
    mut_parser.add_argument("--files", type=str, required=True, help="Comma-separated list of modified files")
    mut_parser.add_argument("--diff", type=str, default="", help="Diff summary")
    mut_parser.add_argument("--added", type=int, default=0, help="Lines added")
    mut_parser.add_argument("--deleted", type=int, default=0, help="Lines deleted")

    # 4. verify
    ver_parser = subparsers.add_parser("verify", help="Record test verification result")
    ver_parser.add_argument("--command", type=str, required=True, help="Verification command executed")
    ver_parser.add_argument("--exit-code", type=int, default=0, help="Command exit code")
    ver_parser.add_argument("--summary", type=str, default="", help="Summary of output or error")
    ver_parser.add_argument("--passed", action="store_true", default=False, help="Whether verification passed")

    # 5. decision
    dec_parser = subparsers.add_parser("decision", help="Record decision outcome")
    dec_parser.add_argument("--status", type=str, required=True, choices=["CONFIRMED", "REVERTED", "PIVOTED", "ABANDONED"], help="Decision status")
    dec_parser.add_argument("--rationale", type=str, required=True, help="Justification for decision")

    # 6. timeline
    subparsers.add_parser("timeline", help="Display chronological decision tree timeline")

    # 7. resume
    resume_parser = subparsers.add_parser("resume", help="Generate zero-loss resume token and prompt context")
    resume_parser.add_argument("--json", action="store_true", help="Output as JSON token envelope")

    # 8. mcp
    subparsers.add_parser("mcp", help="Launch Model Context Protocol (MCP) stdio server")

    args = parser.parse_args(argv)

    if args.subcommand == "init":
        os.makedirs(args.dir, exist_ok=True)
        print(f"[+] Initialized Agent-Blackbox flight data storage at {args.dir}/")
        return 0

    recorder = FlightRecorder(storage_dir=args.dir)

    if args.subcommand == "hypothesis":
        evt = recorder.record_hypothesis(goal=args.goal, hypothesis=args.text, confidence=args.confidence)
        print(f"[+] Recorded HYPOTHESIS: {evt.event_id}")
        return 0

    elif args.subcommand == "mutation":
        files = [f.strip() for f in args.files.split(",") if f.strip()]
        evt = recorder.record_mutation(files_changed=files, diff_summary=args.diff, lines_added=args.added, lines_deleted=args.deleted)
        print(f"[+] Recorded MUTATION: {evt.event_id} ({len(files)} files)")
        return 0

    elif args.subcommand == "verify":
        evt = recorder.record_verification(command=args.command, exit_code=args.exit_code, summary=args.summary, passed=args.passed)
        status_label = "PASSED" if args.passed else "FAILED"
        print(f"[+] Recorded VERIFICATION: {evt.event_id} ({status_label})")
        return 0

    elif args.subcommand == "decision":
        evt = recorder.record_decision(status=args.status, rationale=args.rationale)
        print(f"[+] Recorded DECISION: {evt.event_id} ({args.status.upper()})")
        return 0

    elif args.subcommand == "timeline":
        events = recorder.get_events()
        print(render_timeline(events))
        return 0

    elif args.subcommand == "resume":
        events = recorder.get_events()
        token_data = generate_resume_token(events)
        if args.json:
            print(json.dumps(token_data, indent=2))
        else:
            print(token_data["prompt_block"])
        return 0

    elif args.subcommand == "mcp":
        run_mcp_server()
        return 0

    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
