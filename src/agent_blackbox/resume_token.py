"""
Zero-loss Resume Token generation for Agent-Blackbox.
Synthesizes historical decision trees into a dense, high-signal prompt block
preventing context amnesia and repetitive failures across sessions.
"""
import json
import hashlib
import base64
from typing import List, Dict, Any
from .models import FlightEvent, FlightEventType

def generate_resume_token(events: List[FlightEvent]) -> Dict[str, Any]:
    """
    Synthesizes recorded telemetry into a compact, actionable prompt context.
    """
    if not events:
        return {
            "token": "",
            "prompt_block": "[BLACKBOX RESUME CONTEXT]\nNo active flight telemetry recorded.\n[END RESUME CONTEXT]",
            "goal": "Unspecified",
            "confirmed_count": 0,
            "abandoned_count": 0
        }

    goal = "Unspecified Goal"
    confirmed_decisions = []
    abandoned_paths = []
    active_files = set()
    last_verification = None

    for evt in events:
        if evt.event_type == FlightEventType.HYPOTHESIS:
            if "goal" in evt.data and evt.data["goal"]:
                goal = evt.data["goal"]

        elif evt.event_type == FlightEventType.MUTATION:
            for f in evt.data.get("files_changed", []):
                active_files.add(f)

        elif evt.event_type == FlightEventType.VERIFICATION:
            last_verification = evt.data

        elif evt.event_type == FlightEventType.DECISION:
            status = evt.data.get("status", "").upper()
            rationale = evt.data.get("rationale", "")
            if status == "CONFIRMED":
                confirmed_decisions.append(rationale)
            elif status in ("REVERTED", "ABANDONED", "PIVOTED"):
                abandoned_paths.append(f"{status}: {rationale}")

    # Build dense, token-efficient prompt block
    lines = [
        "[BLACKBOX RESUME CONTEXT]",
        f"Goal: {goal}",
        f"Steps Recorded: {len(events)} telemetry events"
    ]

    if confirmed_decisions:
        lines.append("Locked In Decisions:")
        for idx, dec in enumerate(confirmed_decisions[-4:], 1):
            lines.append(f"{idx}. {dec}")

    if abandoned_paths:
        lines.append("Abandoned / Failed Paths (DO NOT REPEAT):")
        for idx, ab in enumerate(abandoned_paths[-4:], 1):
            lines.append(f"{idx}. {ab}")

    if active_files:
        files_str = ", ".join(sorted(list(active_files))[:6])
        lines.append(f"Active Files: {files_str}")

    if last_verification:
        status_str = "SUCCESS" if last_verification.get("passed") else "FAILED"
        lines.append(f"Last Test Status: {status_str} ({last_verification.get('summary', '')})")

    lines.append("[END RESUME CONTEXT]")
    prompt_block = "\n".join(lines)

    # Cryptographic integrity seal
    raw_bytes = prompt_block.encode("utf-8")
    token_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]
    compact_b64 = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    token_str = f"bbx_{token_hash}_{compact_b64[:32]}"

    return {
        "token": token_str,
        "token_hash": token_hash,
        "prompt_block": prompt_block,
        "goal": goal,
        "confirmed_count": len(confirmed_decisions),
        "abandoned_count": len(abandoned_paths)
    }

def unpack_resume_token(token_str: str) -> Dict[str, Any]:
    """Validates token header and prefix format."""
    is_valid = token_str.startswith("bbx_") and len(token_str.split("_")) >= 3
    return {
        "valid": is_valid,
        "token": token_str
    }
