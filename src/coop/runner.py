"""
runner.py — Core agent execution engine.

Loads a manifest, executes the script, emits typed Events.
Does not know about HTTP, terminals, or any transport.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Callable, Dict, Any, Iterator, List, Optional, Union

from .events import Event, EventType
from .manifest import Manifest, ManifestError


EventCallback = Callable[[Event], None]


class RunnerError(RuntimeError):
    pass


class AgentRunner:
    def __init__(self, manifest: Manifest):
        self.manifest = manifest

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "AgentRunner":
        return cls(Manifest.load(path))

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(
        self,
        input_data: Optional[Dict[str, Any]] = None,
        on_event: Optional[EventCallback] = None,
    ) -> int:
        """
        Execute the agent script and stream events.

        Args:
            input_data: dict passed to the agent as AGENT_INPUT env var.
            on_event:   callback invoked for every Event. If None, events
                        are silently collected and returned via iter_events.

        Returns:
            exit code from the agent script.
        """
        input_data = input_data or {}

        if not self.manifest.validate_input(input_data):
            e = Event.error(self.manifest.id, "Input validation failed")
            if on_event:
                on_event(e)
            return 1

        script = self.manifest.script
        if not script or not script.exists():
            e = Event.error(self.manifest.id, f"Script not found: {script}")
            if on_event:
                on_event(e)
            return 1

        if on_event:
            on_event(Event.start(self.manifest.id, self.manifest.title))

        env = os.environ.copy()
        env["AGENT_ID"] = self.manifest.id
        env["AGENT_INPUT"] = json.dumps(input_data)

        try:
            proc = subprocess.Popen(
                ["bash", str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            for line in proc.stdout:
                line = line.rstrip("\n")
                if not line:
                    continue
                event = self._parse_line(line)
                if on_event:
                    on_event(event)

            exit_code = proc.wait()

            if on_event:
                on_event(Event.exit(self.manifest.id, exit_code))

            return exit_code

        except Exception as exc:
            if on_event:
                on_event(Event.error(self.manifest.id, str(exc)))
            return 1

    def iter_events(
        self,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Event]:
        """Run the agent and yield events one by one."""
        events: list[Event] = []

        def collect(e: Event):
            events.append(e)

        # We need streaming, not buffered — run in a generator-friendly way
        input_data = input_data or {}

        if not self.manifest.validate_input(input_data):
            yield Event.error(self.manifest.id, "Input validation failed")
            return

        script = self.manifest.script
        if not script or not script.exists():
            yield Event.error(self.manifest.id, f"Script not found: {script}")
            return

        yield Event.start(self.manifest.id, self.manifest.title)

        env = os.environ.copy()
        env["AGENT_ID"] = self.manifest.id
        env["AGENT_INPUT"] = json.dumps(input_data)

        try:
            proc = subprocess.Popen(
                ["bash", str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            for line in proc.stdout:
                line = line.rstrip("\n")
                if line:
                    yield self._parse_line(line)

            exit_code = proc.wait()
            yield Event.exit(self.manifest.id, exit_code)

        except Exception as exc:
            yield Event.error(self.manifest.id, str(exc))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_line(self, line: str) -> Event:
        """Parse a line from the agent script into an Event."""
        try:
            data = json.loads(line)
            # If the script emits a valid event dict, use it
            if "event" in data:
                return Event.from_dict({**data, "agent": self.manifest.id})
            # Otherwise treat it as structured data
            return Event.data(self.manifest.id, data)
        except json.JSONDecodeError:
            return Event.output(self.manifest.id, line)
