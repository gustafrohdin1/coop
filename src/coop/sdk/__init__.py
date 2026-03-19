"""
coop.sdk — Base classes for building agents and handlers.

Extend these to build on top of coop:

    from coop.sdk import BaseAgent, BaseHandler
"""

from .agent import BaseAgent
from .handler import BaseHandler
from .registry import Registry

__all__ = ["BaseAgent", "BaseHandler", "Registry"]
