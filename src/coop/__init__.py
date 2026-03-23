"""
coop — Cooperative agent SDK.

Core imports:
    from coop import ScriptRunner
    from coop.sdk import BaseAgent, BaseHandler
    from coop.events import Event, EventType
"""

from .runner import ScriptRunner
from .manifest import Manifest
from .events import Event, EventType

__version__ = "0.1.0"
__all__ = ["ScriptRunner", "Manifest", "Event", "EventType"]
