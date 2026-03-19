"""
events.py — The locked event contract.

Every agent emits events. Every handler consumes events.
This is the single source of truth for event structure.

Event types:
    start   — agent execution began
    output  — a line of output from the agent
    data    — structured JSON data from the agent
    error   — an error occurred
    exit    — agent finished, with exit code
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time


class EventType(str, Enum):
    START  = "start"
    OUTPUT = "output"
    DATA   = "data"
    ERROR  = "error"
    EXIT   = "exit"


@dataclass
class Event:
    type: EventType
    agent_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def start(cls, agent_id: str, title: str) -> "Event":
        return cls(type=EventType.START, agent_id=agent_id, payload={"title": title})

    @classmethod
    def output(cls, agent_id: str, line: str) -> "Event":
        return cls(type=EventType.OUTPUT, agent_id=agent_id, payload={"line": line})

    @classmethod
    def data(cls, agent_id: str, data: Dict[str, Any]) -> "Event":
        return cls(type=EventType.DATA, agent_id=agent_id, payload=data)

    @classmethod
    def error(cls, agent_id: str, msg: str) -> "Event":
        return cls(type=EventType.ERROR, agent_id=agent_id, payload={"msg": msg})

    @classmethod
    def exit(cls, agent_id: str, code: int) -> "Event":
        return cls(type=EventType.EXIT, agent_id=agent_id, payload={"code": code})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.type.value,
            "agent": self.agent_id,
            "timestamp": self.timestamp,
            **self.payload,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        event_type = EventType(d["event"])
        agent_id = d.get("agent", "unknown")
        timestamp = d.get("timestamp", time.time())
        payload = {k: v for k, v in d.items()
                   if k not in ("event", "agent", "timestamp")}
        return cls(type=event_type, agent_id=agent_id,
                   payload=payload, timestamp=timestamp)
