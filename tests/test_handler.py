"""
test_handler.py — Test BaseHandler dispatch and ApiHandler collection.

Uses a fake runner that emits a fixed sequence of events —
no bash scripts, no subprocess, no filesystem needed.
"""

import pytest
from src.coop.events import Event, EventType
from src.coop.sdk.handler import BaseHandler
from handlers.api import ApiHandler


# ------------------------------------------------------------------
# Fake runner — emits a fixed event sequence
# ------------------------------------------------------------------

class FakeManifest:
    id = "fake-agent"
    title = "Fake Agent"

    def validate_input(self, _):
        return True


class FakeRunner:
    manifest = FakeManifest()

    def __init__(self, events):
        self._events = events

    def run(self, input_data=None, on_event=None):
        for e in self._events:
            if on_event:
                on_event(e)
        return 0

    def iter_events(self, input_data=None):
        yield from self._events


SAMPLE_EVENTS = [
    Event.start("fake-agent", "Fake Agent"),
    Event.output("fake-agent", "line one"),
    Event.output("fake-agent", "line two"),
    Event.data("fake-agent", {"key": "value"}),
    Event.exit("fake-agent", 0),
]


# ------------------------------------------------------------------
# BaseHandler dispatch
# ------------------------------------------------------------------

class RecordingHandler(BaseHandler):
    def __init__(self):
        self.received = []

    def on_event(self, event):
        self.received.append(event)


def test_handler_receives_all_events():
    handler = RecordingHandler()
    runner = FakeRunner(SAMPLE_EVENTS)
    handler.handle(runner)
    assert len(handler.received) == len(SAMPLE_EVENTS)


def test_handler_dispatch_routes_to_hooks():
    dispatched = []

    class HookHandler(BaseHandler):
        def on_start(self, e):  dispatched.append("start")
        def on_output(self, e): dispatched.append("output")
        def on_data(self, e):   dispatched.append("data")
        def on_exit(self, e):   dispatched.append("exit")
        def on_event(self, e):  dispatched.append("unknown")

    handler = HookHandler()
    for e in SAMPLE_EVENTS:
        handler.dispatch(e)

    assert dispatched == ["start", "output", "output", "data", "exit"]


# ------------------------------------------------------------------
# ApiHandler
# ------------------------------------------------------------------

def test_api_handler_collect():
    handler = ApiHandler()
    runner = FakeRunner(SAMPLE_EVENTS)
    result = handler.collect(runner)

    assert result["agent"] == "fake-agent"
    assert result["exit_code"] == 0
    assert result["output"] == ["line one", "line two"]
    assert result["data"] == [{"key": "value"}]
    assert result["errors"] == []


def test_api_handler_sse():
    handler = ApiHandler()
    runner = FakeRunner(SAMPLE_EVENTS)
    chunks = list(handler.iter_sse(runner))

    assert len(chunks) == len(SAMPLE_EVENTS)
    for chunk in chunks:
        assert chunk.startswith("data: ")
        assert chunk.endswith("\n\n")


def test_api_handler_error_collection():
    events = [
        Event.start("fake-agent", "Fake Agent"),
        Event.error("fake-agent", "something failed"),
        Event.exit("fake-agent", 1),
    ]
    handler = ApiHandler()
    result = handler.collect(FakeRunner(events))

    assert result["exit_code"] == 1
    assert result["errors"] == ["something failed"]


# ------------------------------------------------------------------
# BaseHandler — on_event raises NotImplementedError
# ------------------------------------------------------------------

def test_base_handler_on_event_raises():
    handler = BaseHandler()
    with pytest.raises(NotImplementedError):
        handler.on_event(Event.start("a", "A"))


def test_base_handler_default_on_error_delegates_to_on_event():
    """Default on_error calls on_event, so it also raises NotImplementedError."""
    handler = BaseHandler()
    with pytest.raises(NotImplementedError):
        handler.on_error(Event.error("a", "oops"))


# ------------------------------------------------------------------
# ApiHandler — on_event (unknown event type ignored)
# ------------------------------------------------------------------

def test_api_handler_on_event_ignores_unknown():
    handler = ApiHandler()
    # Calling on_event directly should be a no-op
    handler.on_event(Event.start("a", "A"))  # no exception, no state change
    result = handler._build_result("a")
    assert result["output"] == []
    assert result["errors"] == []
