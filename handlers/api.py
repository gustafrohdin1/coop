"""
handlers/api.py — ApiHandler

Collects coop events for HTTP API responses.
Works with any HTTP framework — returns data, doesn't write to a socket.

For streaming (SSE), use iter_sse().
For request/response, use collect() which returns the full result.

Usage:
    from coop import AgentRunner
    from coop.handlers.api import ApiHandler

    runner = AgentRunner.from_file("agent.json")
    handler = ApiHandler()
    result = handler.collect(runner, input_data={...})
    # result = {"agent": "...", "output": [...], "data": [...], "exit_code": 0}

    # SSE streaming:
    for chunk in handler.iter_sse(runner):
        yield chunk   # each chunk is a text/event-stream line
"""

import json
import time
from typing import Any, Dict, Generator, List, Optional

from coop.sdk.handler import BaseHandler
from coop.events import Event, EventType


class ApiHandler(BaseHandler):
    def __init__(self):
        self._reset()

    def _reset(self):
        self._output_lines: List[str] = []
        self._data_payloads: List[Dict[str, Any]] = []
        self._errors: List[str] = []
        self._exit_code: Optional[int] = None
        self._started_at: Optional[float] = None
        self._finished_at: Optional[float] = None

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_start(self, event: Event):
        self._started_at = event.timestamp

    def on_output(self, event: Event):
        self._output_lines.append(event.payload.get("line", ""))

    def on_data(self, event: Event):
        self._data_payloads.append(event.payload)

    def on_error(self, event: Event):
        self._errors.append(event.payload.get("msg", "unknown error"))

    def on_exit(self, event: Event):
        self._exit_code = event.payload.get("code", 0)
        self._finished_at = event.timestamp

    def on_event(self, event: Event):
        pass  # unknown event types ignored

    # ------------------------------------------------------------------
    # Collect — run agent, return full result dict
    # ------------------------------------------------------------------

    def collect(
        self,
        runner,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run agent and return a complete result dict."""
        self._reset()
        self.handle(runner, input_data)
        return self._build_result(runner.manifest.id)

    def _build_result(self, agent_id: str) -> Dict[str, Any]:
        duration = None
        if self._started_at and self._finished_at:
            duration = round(self._finished_at - self._started_at, 3)
        return {
            "agent": agent_id,
            "exit_code": self._exit_code,
            "output": self._output_lines,
            "data": self._data_payloads,
            "errors": self._errors,
            "duration_seconds": duration,
        }

    # ------------------------------------------------------------------
    # SSE streaming — yield text/event-stream chunks
    # ------------------------------------------------------------------

    def iter_sse(
        self,
        runner,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Generator[str, None, None]:
        """
        Stream agent events as Server-Sent Events.
        Each yielded string is a complete SSE chunk.

        In FastAPI:
            return StreamingResponse(handler.iter_sse(runner), media_type="text/event-stream")
        """
        for event in runner.iter_events(input_data):
            data = json.dumps(event.to_dict())
            yield f"data: {data}\n\n"
