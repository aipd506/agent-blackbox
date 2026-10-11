"""
Timeline rendering engine for Agent-Blackbox.
Produces structured ASCII and Markdown decision trees of historical flight events.
"""
from typing import List
from .models import FlightEvent, FlightEventType

def render_timeline(events: List[FlightEvent]) -> str:
    """
    Renders chronological decision timeline with branch outcomes.
    """
    if not events:
        return "No flight data recorded in blackbox log."

    lines = [
        "============================================================",
        "             AGENT-BLACKBOX FLIGHT DATA TIMELINE            ",
        "============================================================"
    ]

    for idx, evt in enumerate(events, 1):
        ts = evt.timestamp.split("T")[-1].split(".")[0] if "T" in evt.timestamp else evt.timestamp
        etype = evt.event_type.value
        data = evt.data

        if evt.event_type == FlightEventType.HYPOTHESIS:
            goal = data.get("goal", "")
            hypo = data.get("hypothesis", "")
            conf = data.get("confidence", 0.8)
            lines.append(f"[{ts}] Step {idx:02d} | [HYPOTHESIS] (confidence: {conf:.2f})")
            lines.append(f"    Goal: {goal}")
            lines.append(f"    Proposal: {hypo}")

        elif evt.event_type == FlightEventType.MUTATION:
            files = ", ".join(data.get("files_changed", []))
            added = data.get("lines_added", 0)
            deleted = data.get("lines_deleted", 0)
            diff_sum = data.get("diff_summary", "")
            lines.append(f"[{ts}] Step {idx:02d} | [MUTATION] Files: {files} (+{added}, -{deleted})")
            if diff_sum:
                lines.append(f"    Diff: {diff_sum}")

        elif evt.event_type == FlightEventType.VERIFICATION:
            cmd = data.get("command", "")
            code = data.get("exit_code", 0)
            status = "PASSED" if data.get("passed") else "FAILED"
            summary = data.get("summary", "")
            lines.append(f"[{ts}] Step {idx:02d} | [VERIFICATION] {status} (exit {code}): `{cmd}`")
            if summary:
                lines.append(f"    Result: {summary}")

        elif evt.event_type == FlightEventType.DECISION:
            status = data.get("status", "DECIDED")
            rationale = data.get("rationale", "")
            lines.append(f"[{ts}] Step {idx:02d} | [DECISION] >>> {status} <<<")
            lines.append(f"    Rationale: {rationale}")

        lines.append("------------------------------------------------------------")

    return "\n".join(lines)
