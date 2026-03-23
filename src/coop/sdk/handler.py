"""
sdk/handler.py — BaseHandler: extend this to build a coop handler.

A handler consumes the event stream from ScriptRunner.
It doesn't care how the agent runs — only about the events it receives.

Traffic types that become handlers:
    - Terminal  (render events to stdout)
    - API       (stream events as SSE or collect as JSON response)
    - WebSocket (push events to connected clients)
    - Test      (collect events for assertions)
"""

from typing import List
from ..events import Event, EventType


class BaseHandler:
    """
    Extend BaseHandler to consume coop events for any traffic type.

    Subclasses must implement `on_event(event)`.
    Optionally override lifecycle hooks: `on_start`, `on_exit`, `on_error`.
    """

    # ------------------------------------------------------------------
    # Core interface — override these
    # ------------------------------------------------------------------

    def on_event(self, event: Event):
        """Called for every event. Override in subclass."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Lifecycle hooks — override as needed
    # ------------------------------------------------------------------

    def on_start(self, event: Event):
        self.on_event(event)

    def on_output(self, event: Event):
        self.on_event(event)

    def on_data(self, event: Event):
        self.on_event(event)

    def on_error(self, event: Event):
        self.on_event(event)

    def on_exit(self, event: Event):
        self.on_event(event)

    # ------------------------------------------------------------------
    # Dispatch — routes events to lifecycle hooks
    # ------------------------------------------------------------------

    def dispatch(self, event: Event):
        """Route an event to the correct lifecycle hook."""
        dispatch_map = {
            EventType.START:  self.on_start,
            EventType.OUTPUT: self.on_output,
            EventType.DATA:   self.on_data,
            EventType.ERROR:  self.on_error,
            EventType.EXIT:   self.on_exit,
        }
        handler_fn = dispatch_map.get(event.type, self.on_event)
        handler_fn(event)

    # ------------------------------------------------------------------
    # Convenience: run a runner through this handler
    # ------------------------------------------------------------------

    def handle(self, runner, input_data=None):
        """Run an ScriptRunner and dispatch all events through this handler."""
        return runner.run(input_data=input_data, on_event=self.dispatch)
