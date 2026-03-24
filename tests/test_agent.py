"""
test_agent.py — Test BaseAgent lifecycle and emit helpers.
"""

import pytest
from src.coop.events import Event, EventType
from src.coop.manifest import Manifest
from src.coop.sdk.agent import BaseAgent


MINIMAL_MANIFEST = {"id": "test-agent", "version": "1.0.0", "title": "Test Agent"}


def make_manifest():
    return Manifest(MINIMAL_MANIFEST)


# ------------------------------------------------------------------
# Concrete agent for testing
# ------------------------------------------------------------------

class EchoAgent(BaseAgent):
    def execute(self, input_data):
        self.emit_output(f"got: {input_data.get('msg', '')}")
        self.emit_data({"echo": input_data.get("msg", "")})
        return 0


class ErrorAgent(BaseAgent):
    def execute(self, input_data):
        self.emit_error("something broke")
        return 1


class ExceptionAgent(BaseAgent):
    def execute(self, input_data):
        raise RuntimeError("crash!")


# ------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------

def test_id_property():
    agent = EchoAgent(make_manifest())
    assert agent.id == "test-agent"


# ------------------------------------------------------------------
# execute raises NotImplementedError on base class
# ------------------------------------------------------------------

def test_execute_not_implemented():
    agent = BaseAgent(make_manifest())
    with pytest.raises(NotImplementedError):
        agent.execute({})


# ------------------------------------------------------------------
# emit helpers
# ------------------------------------------------------------------

def test_emit_output():
    agent = EchoAgent(make_manifest())
    agent._events = []
    agent.emit_output("hello")
    assert len(agent._events) == 1
    assert agent._events[0].type == EventType.OUTPUT
    assert agent._events[0].payload["line"] == "hello"


def test_emit_data():
    agent = EchoAgent(make_manifest())
    agent._events = []
    agent.emit_data({"x": 42})
    assert len(agent._events) == 1
    assert agent._events[0].type == EventType.DATA
    assert agent._events[0].payload["x"] == 42


def test_emit_error():
    agent = EchoAgent(make_manifest())
    agent._events = []
    agent.emit_error("bad")
    assert len(agent._events) == 1
    assert agent._events[0].type == EventType.ERROR
    assert agent._events[0].payload["msg"] == "bad"


# ------------------------------------------------------------------
# run()
# ------------------------------------------------------------------

def test_run_returns_events_in_order():
    agent = EchoAgent(make_manifest())
    events = agent.run({"msg": "hi"})
    types = [e.type for e in events]
    assert types[0] == EventType.START
    assert types[-1] == EventType.EXIT
    assert EventType.OUTPUT in types
    assert EventType.DATA in types


def test_run_start_event_has_title():
    agent = EchoAgent(make_manifest())
    events = agent.run()
    start = events[0]
    assert start.type == EventType.START
    assert start.payload["title"] == "Test Agent"


def test_run_exit_code_zero_on_success():
    agent = EchoAgent(make_manifest())
    events = agent.run()
    exit_event = events[-1]
    assert exit_event.type == EventType.EXIT
    assert exit_event.payload["code"] == 0


def test_run_exit_code_nonzero_on_failure():
    agent = ErrorAgent(make_manifest())
    events = agent.run()
    exit_event = events[-1]
    assert exit_event.payload["code"] == 1


def test_run_exception_emits_error_and_exits_1():
    agent = ExceptionAgent(make_manifest())
    events = agent.run()
    types = [e.type for e in events]
    assert EventType.ERROR in types
    exit_event = events[-1]
    assert exit_event.payload["code"] == 1
    error_event = next(e for e in events if e.type == EventType.ERROR)
    assert "crash!" in error_event.payload["msg"]


def test_run_with_no_input():
    agent = EchoAgent(make_manifest())
    events = agent.run()
    # Should not raise; input defaults to {}
    assert events[0].type == EventType.START


def test_run_resets_events_on_each_call():
    agent = EchoAgent(make_manifest())
    agent.run({"msg": "first"})
    events = agent.run({"msg": "second"})
    # Only events from the second run should be present
    output_events = [e for e in events if e.type == EventType.OUTPUT]
    assert len(output_events) == 1
    assert "second" in output_events[0].payload["line"]
