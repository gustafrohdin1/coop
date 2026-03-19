"""
coop — Cooperative agent SDK.

Core imports:
    from coop import AgentRunner
    from coop.sdk import BaseAgent, BaseHandler
    from coop.events import Event, EventType
"""

from .runner import AgentRunner
from .manifest import Manifest
from .events import Event, EventType

__version__ = "0.1.0"
__all__ = ["AgentRunner", "Manifest", "Event", "EventType"]
