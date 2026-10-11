"""
Data models and event definitions for Agent-Blackbox.
"""
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class FlightEventType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    MUTATION = "MUTATION"
    VERIFICATION = "VERIFICATION"
    DECISION = "DECISION"

@dataclass
class FlightEvent:
    event_id: str
    event_type: FlightEventType
    session_id: str
    timestamp: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FlightEvent":
        return cls(
            event_id=d["event_id"],
            event_type=FlightEventType(d["event_type"]),
            session_id=d["session_id"],
            timestamp=d["timestamp"],
            data=d.get("data", {})
        )
