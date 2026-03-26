"""
test_runner.py — Test AgentRunner execution, event streaming, and line parsing.

Uses temporary bash scripts and mocking to avoid external dependencies.
"""

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import pytest

from src.coop.events import Event, EventType
from src.coop.manifest import Manifest
from src.coop.runner import AgentRunner


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def make_manifest(data: dict, base_dir: Path = None) -> Manifest:
    return Manifest(data, base_dir=base_dir)


def minimal_manifest(script: str = None, base_dir: Path = None) -> Manifest:
    data = {"id": "run-agent", "version": "1.0.0", "title": "Run Agent"}
    if script:
        data["script"] = script
    return make_manifest(data, base_dir=base_dir)


def write_script(tmp_path: Path, content: str, name: str = "agent.sh") -> Path:
    """Write an executable bash script to tmp_path and return its Path."""
    script = tmp_path / name
    script.write_text(content)
    script.chmod(0o755)
    return script


# ------------------------------------------------------------------
# from_file
# ------------------------------------------------------------------

def test_from_file(tmp_path):
    manifest_file = tmp_path / "agent.json"
    manifest_file.write_text(json.dumps({
        "id": "file-agent", "version": "1.0.0", "title": "File Agent",
        "script": "run.sh"
    }))
    runner = AgentRunner.from_file(manifest_file)
    assert runner.manifest.id == "file-agent"
    assert isinstance(runner, AgentRunner)


# ------------------------------------------------------------------
# run() — no script configured
# ------------------------------------------------------------------

def test_run_no_script_emits_error():
    manifest = minimal_manifest()  # no script field
    runner = AgentRunner(manifest)
    events = []
    code = runner.run(on_event=events.append)
    assert code == 1
    assert any(e.type == EventType.ERROR for e in events)
    error = next(e for e in events if e.type == EventType.ERROR)
    assert "Script not found" in error.payload["msg"]


def test_run_script_not_found_on_disk(tmp_path):
    manifest = minimal_manifest(script="missing.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    code = runner.run(on_event=events.append)
    assert code == 1
    assert any(e.type == EventType.ERROR for e in events)


# ------------------------------------------------------------------
# run() — success path with a real bash script
# ------------------------------------------------------------------

def test_run_emits_start_and_exit(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho 'hello'\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    code = runner.run(on_event=events.append)
    assert code == 0
    assert events[0].type == EventType.START
    assert events[-1].type == EventType.EXIT
    assert events[-1].payload["code"] == 0


def test_run_plain_output_lines(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho 'line one'\necho 'line two'\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    runner.run(on_event=events.append)
    output_lines = [e.payload["line"] for e in events if e.type == EventType.OUTPUT]
    assert "line one" in output_lines
    assert "line two" in output_lines


def test_run_json_data_line(tmp_path):
    write_script(tmp_path, '#!/bin/bash\necho \'{"x": 42}\'\n')
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    runner.run(on_event=events.append)
    data_events = [e for e in events if e.type == EventType.DATA]
    assert any(e.payload.get("x") == 42 for e in data_events)


def test_run_json_event_line(tmp_path):
    payload = json.dumps({"event": "output", "line": "from-script"})
    write_script(tmp_path, f'#!/bin/bash\necho \'{payload}\'\n')
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    runner.run(on_event=events.append)
    output_events = [e for e in events if e.type == EventType.OUTPUT]
    assert any(e.payload.get("line") == "from-script" for e in output_events)


def test_run_nonzero_exit_code(tmp_path):
    write_script(tmp_path, "#!/bin/bash\nexit 42\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    code = runner.run(on_event=events.append)
    assert code == 42
    exit_event = next(e for e in events if e.type == EventType.EXIT)
    assert exit_event.payload["code"] == 42


def test_run_sets_agent_env_vars(tmp_path):
    write_script(tmp_path, '#!/bin/bash\necho "$AGENT_ID"\necho "$AGENT_INPUT"\n')
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    runner.run(input_data={"key": "val"}, on_event=events.append)
    output_lines = [e.payload.get("line", "") for e in events if e.type == EventType.OUTPUT]
    assert "run-agent" in output_lines
    # AGENT_INPUT is JSON, so it is parsed as a DATA event by _parse_line
    data_events = [e for e in events if e.type == EventType.DATA]
    assert any(e.payload.get("key") == "val" for e in data_events)


def test_run_no_on_event_still_returns_code(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho 'silent'\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    code = runner.run()
    assert code == 0


# ------------------------------------------------------------------
# run() — exception path
# ------------------------------------------------------------------

def test_run_subprocess_exception_emits_error(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho hi\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    with patch("src.coop.runner.subprocess.Popen", side_effect=OSError("popen failed")):
        code = runner.run(on_event=events.append)
    assert code == 1
    assert any(e.type == EventType.ERROR for e in events)
    error = next(e for e in events if e.type == EventType.ERROR)
    assert "popen failed" in error.payload["msg"]


# ------------------------------------------------------------------
# iter_events()
# ------------------------------------------------------------------

def test_iter_events_no_script():
    manifest = minimal_manifest()
    runner = AgentRunner(manifest)
    events = list(runner.iter_events())
    assert len(events) == 1
    assert events[0].type == EventType.ERROR


def test_iter_events_script_not_on_disk(tmp_path):
    manifest = minimal_manifest(script="ghost.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = list(runner.iter_events())
    assert events[0].type == EventType.ERROR


def test_iter_events_success(tmp_path):
    write_script(tmp_path, '#!/bin/bash\necho "streamed"\n')
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = list(runner.iter_events())
    assert events[0].type == EventType.START
    assert events[-1].type == EventType.EXIT
    output = [e.payload.get("line") for e in events if e.type == EventType.OUTPUT]
    assert "streamed" in output


def test_iter_events_exception(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho hi\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    with patch("src.coop.runner.subprocess.Popen", side_effect=OSError("iter fail")):
        events = list(runner.iter_events())
    assert any(e.type == EventType.ERROR for e in events)


# ------------------------------------------------------------------
# _parse_line
# ------------------------------------------------------------------

def test_parse_line_plain_text():
    runner = AgentRunner(minimal_manifest())
    e = runner._parse_line("plain text")
    assert e.type == EventType.OUTPUT
    assert e.payload["line"] == "plain text"


def test_parse_line_json_data():
    runner = AgentRunner(minimal_manifest())
    e = runner._parse_line('{"score": 99}')
    assert e.type == EventType.DATA
    assert e.payload["score"] == 99


def test_parse_line_json_event():
    runner = AgentRunner(minimal_manifest())
    e = runner._parse_line('{"event": "output", "line": "hi"}')
    assert e.type == EventType.OUTPUT
    assert e.payload["line"] == "hi"


def test_parse_line_empty_json_object():
    runner = AgentRunner(minimal_manifest())
    e = runner._parse_line("{}")
    assert e.type == EventType.DATA


def test_parse_line_invalid_json():
    runner = AgentRunner(minimal_manifest())
    e = runner._parse_line("not { valid } json")
    assert e.type == EventType.OUTPUT


# ------------------------------------------------------------------
# run() — input validation failure (validate_input returns False)
# ------------------------------------------------------------------

def test_run_input_validation_failure_with_callback(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho hi\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    with patch.object(manifest, "validate_input", return_value=False):
        runner = AgentRunner(manifest)
        events = []
        code = runner.run(input_data={}, on_event=events.append)
    assert code == 1
    assert any(e.type == EventType.ERROR for e in events)
    assert "Input validation failed" in events[0].payload["msg"]


def test_run_input_validation_failure_no_callback(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho hi\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    with patch.object(manifest, "validate_input", return_value=False):
        runner = AgentRunner(manifest)
        code = runner.run(input_data={})
    assert code == 1


# ------------------------------------------------------------------
# run() — blank lines in stdout are skipped
# ------------------------------------------------------------------

def test_run_skips_blank_output_lines(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho ''\necho 'real line'\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    runner = AgentRunner(manifest)
    events = []
    runner.run(on_event=events.append)
    # blank line should not produce an output event
    output_lines = [e.payload.get("line") for e in events if e.type == EventType.OUTPUT]
    assert "" not in output_lines
    assert "real line" in output_lines


# ------------------------------------------------------------------
# iter_events() — input validation failure
# ------------------------------------------------------------------

def test_iter_events_input_validation_failure(tmp_path):
    write_script(tmp_path, "#!/bin/bash\necho hi\n")
    manifest = minimal_manifest(script="agent.sh", base_dir=tmp_path)
    with patch.object(manifest, "validate_input", return_value=False):
        runner = AgentRunner(manifest)
        events = list(runner.iter_events())
    assert len(events) == 1
    assert events[0].type == EventType.ERROR
    assert "Input validation failed" in events[0].payload["msg"]
