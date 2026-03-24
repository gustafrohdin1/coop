"""
test_terminal.py — Test TerminalHandler output rendering.
"""

import io
import json
import sys
import pytest
from src.coop.events import Event, EventType
from handlers.terminal import TerminalHandler


def _make_handler(stream=None, **kwargs):
    buf = stream or io.StringIO()
    return TerminalHandler(stream=buf, **kwargs), buf


def _make_err_handler():
    """Handler that captures stdout and allows stderr inspection."""
    buf = io.StringIO()
    return TerminalHandler(stream=buf), buf


# ------------------------------------------------------------------
# on_start
# ------------------------------------------------------------------

def test_on_start_writes_title():
    handler, buf = _make_handler()
    handler.on_start(Event.start("a", "My Agent"))
    assert "My Agent" in buf.getvalue()
    assert "▶" in buf.getvalue()


def test_on_start_uses_agent_id_when_no_title():
    handler, buf = _make_handler()
    e = Event(type=EventType.START, agent_id="fallback-agent", payload={})
    handler.on_start(e)
    assert "fallback-agent" in buf.getvalue()


# ------------------------------------------------------------------
# on_output
# ------------------------------------------------------------------

def test_on_output_writes_line():
    handler, buf = _make_handler()
    handler.on_output(Event.output("a", "hello world"))
    assert "hello world" in buf.getvalue()


def test_on_output_empty_line():
    handler, buf = _make_handler()
    handler.on_output(Event.output("a", ""))
    # empty string should still produce a newline from print
    assert buf.getvalue() == "\n"


# ------------------------------------------------------------------
# on_data
# ------------------------------------------------------------------

def test_on_data_writes_json():
    handler, buf = _make_handler()
    handler.on_data(Event.data("a", {"x": 1, "y": [2, 3]}))
    output = buf.getvalue()
    parsed = json.loads(output.strip())
    assert parsed == {"x": 1, "y": [2, 3]}


# ------------------------------------------------------------------
# on_error
# ------------------------------------------------------------------

def test_on_error_writes_to_stderr(capsys):
    handler = TerminalHandler()
    handler.on_error(Event.error("a", "boom"))
    captured = capsys.readouterr()
    assert "boom" in captured.err
    assert "✗" in captured.err


def test_on_error_unknown_msg(capsys):
    handler = TerminalHandler()
    e = Event(type=EventType.ERROR, agent_id="a", payload={})
    handler.on_error(e)
    captured = capsys.readouterr()
    assert "unknown error" in captured.err


# ------------------------------------------------------------------
# on_exit
# ------------------------------------------------------------------

def test_on_exit_success_writes_done(capsys):
    handler = TerminalHandler()
    handler.on_exit(Event.exit("a", 0))
    captured = capsys.readouterr()
    assert "✓" in captured.out
    assert "done" in captured.out


def test_on_exit_failure_writes_to_stderr(capsys):
    handler = TerminalHandler()
    handler.on_exit(Event.exit("a", 2))
    captured = capsys.readouterr()
    assert "2" in captured.err
    assert "✗" in captured.err


# ------------------------------------------------------------------
# on_event (fallback)
# ------------------------------------------------------------------

def test_on_event_fallback_writes_dict():
    handler, buf = _make_handler()
    e = Event.start("a", "My Agent")
    handler.on_event(e)
    assert "start" in buf.getvalue()


# ------------------------------------------------------------------
# dispatch integration
# ------------------------------------------------------------------

def test_dispatch_routes_all_event_types(capsys):
    handler = TerminalHandler()
    events = [
        Event.start("a", "Title"),
        Event.output("a", "a line"),
        Event.data("a", {"k": "v"}),
        Event.error("a", "oops"),
        Event.exit("a", 0),
    ]
    for e in events:
        handler.dispatch(e)
    captured = capsys.readouterr()
    assert "Title" in captured.out
    assert "a line" in captured.out
    assert "oops" in captured.err


# ------------------------------------------------------------------
# Constructor options
# ------------------------------------------------------------------

def test_show_timestamps_stored():
    handler = TerminalHandler(show_timestamps=True)
    assert handler.show_timestamps is True


def test_default_stream_is_stdout():
    handler = TerminalHandler()
    assert handler.stream is sys.stdout


def test_custom_stream():
    buf = io.StringIO()
    handler = TerminalHandler(stream=buf)
    assert handler.stream is buf


# ------------------------------------------------------------------
# handle integration with fake runner
# ------------------------------------------------------------------

class FakeRunner:
    class manifest:
        id = "t"
    def run(self, input_data=None, on_event=None):
        for e in [Event.start("t", "T"), Event.output("t", "ln"), Event.exit("t", 0)]:
            if on_event:
                on_event(e)
        return 0


def test_handle_integration(capsys):
    handler = TerminalHandler()
    handler.handle(FakeRunner())
    captured = capsys.readouterr()
    assert "T" in captured.out
    assert "ln" in captured.out
    assert "done" in captured.out
