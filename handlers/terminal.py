"""
handlers/terminal.py — TerminalHandler

Renders the coop event stream to the terminal.
Extend or replace format_* methods to customize output.
"""

import sys
from coop.sdk.handler import BaseHandler
from coop.events import Event, EventType


class TerminalHandler(BaseHandler):
    """
    Renders agent events to stdout.

    Usage:
        from coop import AgentRunner
        from coop.handlers.terminal import TerminalHandler

        runner = AgentRunner.from_file("agent.json")
        handler = TerminalHandler()
        handler.handle(runner)
    """

    def __init__(self, stream=None, show_timestamps: bool = False):
        self.stream = stream or sys.stdout
        self.show_timestamps = show_timestamps

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def on_start(self, event: Event):
        title = event.payload.get("title", event.agent_id)
        self._write(f"▶  {title}")

    def on_output(self, event: Event):
        self._write(event.payload.get("line", ""))

    def on_data(self, event: Event):
        import json
        self._write(json.dumps(event.payload, indent=2))

    def on_error(self, event: Event):
        msg = event.payload.get("msg", "unknown error")
        self._write(f"✗  {msg}", file=sys.stderr)

    def on_exit(self, event: Event):
        code = event.payload.get("code", 0)
        if code == 0:
            self._write(f"✓  done")
        else:
            self._write(f"✗  exited with code {code}", file=sys.stderr)

    def on_event(self, event: Event):
        # Fallback for unknown event types
        self._write(str(event.to_dict()))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _write(self, msg: str, file=None):
        out = file or self.stream
        print(msg, file=out)
        out.flush()
