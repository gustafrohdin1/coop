"""
sdk/agent.py — BaseAgent: extend this to build a coop agent.

A BaseAgent wraps a Manifest and provides a clean interface
for emitting events without knowing about the transport.
"""

from typing import Any, Dict, Optional
from ..events import Event, EventType
from ..manifest import Manifest


class BaseAgent:
    """
    Extend BaseAgent to implement a coop agent in pure Python
    (as an alternative to bash scripts).

    Subclasses must implement `execute()`.
    """

    def __init__(self, manifest: Manifest):
        self.manifest = manifest
        self._events: list[Event] = []

    @property
    def id(self) -> str:
        return self.manifest.id

    # ------------------------------------------------------------------
    # Emit helpers — call these inside execute()
    # ------------------------------------------------------------------

    def emit_output(self, line: str):
        self._events.append(Event.output(self.id, line))

    def emit_data(self, data: Dict[str, Any]):
        self._events.append(Event.data(self.id, data))

    def emit_error(self, msg: str):
        self._events.append(Event.error(self.id, msg))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def execute(self, input_data: Dict[str, Any]) -> int:
        """
        Override in subclass. Emit events via self.emit_*().
        Return exit code (0 = success).
        """
        raise NotImplementedError

    def run(self, input_data: Optional[Dict[str, Any]] = None):
        """Run the agent and return all emitted events."""
        input_data = input_data or {}
        self._events = [Event.start(self.id, self.manifest.title)]
        try:
            code = self.execute(input_data)
        except Exception as exc:
            self.emit_error(str(exc))
            code = 1
        self._events.append(Event.exit(self.id, code))
        return self._events
