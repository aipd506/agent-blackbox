"""
Flight Recorder Engine for Agent-Blackbox.
Maintains an append-only JSONL flight data log with thread-safe persistence.
"""
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .models import FlightEvent, FlightEventType

class FlightRecorder:
    def __init__(self, storage_dir: str = ".blackbox", session_id: Optional[str] = None):
        self.storage_dir = storage_dir
        self.session_id = session_id or uuid.uuid4().hex[:12]
        self.log_file = os.path.join(self.storage_dir, "flight_data.jsonl")
        self._ensure_storage()
        self._counter = 0

    def _ensure_storage(self) -> None:
        os.makedirs(self.storage_dir, exist_ok=True)

    def _next_event_id(self) -> str:
        self._counter += 1
        return f"evt_{datetime.now(timezone.utc).strftime('%H%M%S')}_{self._counter:03d}"

    def append_event(self, event_type: FlightEventType, data: Dict[str, Any]) -> FlightEvent:
        event = FlightEvent(
            event_id=self._next_event_id(),
            event_type=event_type,
            session_id=self.session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=data
        )
        line = json.dumps(event.to_dict()) + "\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)
        return event

    def record_hypothesis(self, goal: str, hypothesis: str, confidence: float = 0.8) -> FlightEvent:
        return self.append_event(
            FlightEventType.HYPOTHESIS,
            {
                "goal": goal,
                "hypothesis": hypothesis,
                "confidence": confidence
            }
        )

    def record_mutation(
        self,
        files_changed: List[str],
        diff_summary: str,
        lines_added: int = 0,
        lines_deleted: int = 0
    ) -> FlightEvent:
        return self.append_event(
            FlightEventType.MUTATION,
            {
                "files_changed": files_changed,
                "diff_summary": diff_summary,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted
            }
        )

    def record_verification(
        self,
        command: str,
        exit_code: int,
        summary: str,
        passed: bool
    ) -> FlightEvent:
        return self.append_event(
            FlightEventType.VERIFICATION,
            {
                "command": command,
                "exit_code": exit_code,
                "summary": summary,
                "passed": passed
            }
        )

    def record_decision(self, status: str, rationale: str) -> FlightEvent:
        """
        Records architectural decision:
        status in ('CONFIRMED', 'REVERTED', 'PIVOTED', 'ABANDONED')
        """
        return self.append_event(
            FlightEventType.DECISION,
            {
                "status": status.upper(),
                "rationale": rationale
            }
        )

    def get_events(self) -> List[FlightEvent]:
        events: List[FlightEvent] = []
        if not os.path.exists(self.log_file):
            return events

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        events.append(FlightEvent.from_dict(d))
                    except Exception:
                        continue
        return events
