"""
agent-blackbox: The Deterministic Flight Data Recorder for Autonomous Coding Sessions.
"""

__version__ = "0.1.0"
__author__ = "aipd506"

from .models import FlightEvent, FlightEventType
from .recorder import FlightRecorder
from .resume_token import generate_resume_token, unpack_resume_token
from .timeline import render_timeline

__all__ = [
    "FlightEvent",
    "FlightEventType",
    "FlightRecorder",
    "generate_resume_token",
    "unpack_resume_token",
    "render_timeline",
    "__version__"
]
