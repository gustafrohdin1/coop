"""
test_events.py — Test the event contract.
"""

import pytest
from src.coop.events import Event, EventType


def test_start_event():
    e = Event.start("my-agent", "My Agent")
    assert e.type == EventType.START
    assert e.agent_id == "my-agent"
    assert e.payload["title"] == "My Agent"


def test_output_event():
    e = Event.output("my-agent", "hello world")
    assert e.type == EventType.OUTPUT
    assert e.payload["line"] == "hello world"


def test_data_event():
    e = Event.data("my-agent", {"key": "value"})
    assert e.type == EventType.DATA
    assert e.payload["key"] == "value"


def test_error_event():
    e = Event.error("my-agent", "something went wrong")
    assert e.type == EventType.ERROR
    assert e.payload["msg"] == "something went wrong"


def test_exit_event():
    e = Event.exit("my-agent", 0)
    assert e.type == EventType.EXIT
    assert e.payload["code"] == 0


def test_to_dict():
    e = Event.start("my-agent", "My Agent")
    d = e.to_dict()
    assert d["event"] == "start"
    assert d["agent"] == "my-agent"
    assert d["title"] == "My Agent"
    assert "timestamp" in d


def test_from_dict_roundtrip():
    e = Event.output("my-agent", "a line")
    d = e.to_dict()
    e2 = Event.from_dict(d)
    assert e2.type == e.type
    assert e2.agent_id == e.agent_id
    assert e2.payload == e.payload
