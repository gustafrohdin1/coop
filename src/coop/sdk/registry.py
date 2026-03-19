"""
sdk/registry.py — Handler and agent registry.

Register handlers by name. Look them up at runtime.
Useful for plugin-style architectures where handlers are discovered dynamically.
"""

from typing import Dict, Type
from .handler import BaseHandler
from .agent import BaseAgent


class Registry:
    def __init__(self):
        self._handlers: Dict[str, Type[BaseHandler]] = {}
        self._agents: Dict[str, Type[BaseAgent]] = {}

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def register_handler(self, name: str, handler_cls: Type[BaseHandler]):
        self._handlers[name] = handler_cls

    def get_handler(self, name: str) -> Type[BaseHandler]:
        if name not in self._handlers:
            raise KeyError(f"No handler registered: '{name}'. "
                           f"Available: {list(self._handlers)}")
        return self._handlers[name]

    def handler(self, name: str):
        """Decorator: @registry.handler('terminal')"""
        def decorator(cls: Type[BaseHandler]):
            self.register_handler(name, cls)
            return cls
        return decorator

    # ------------------------------------------------------------------
    # Agents
    # ------------------------------------------------------------------

    def register_agent(self, name: str, agent_cls: Type[BaseAgent]):
        self._agents[name] = agent_cls

    def get_agent(self, name: str) -> Type[BaseAgent]:
        if name not in self._agents:
            raise KeyError(f"No agent registered: '{name}'. "
                           f"Available: {list(self._agents)}")
        return self._agents[name]

    def agent(self, name: str):
        """Decorator: @registry.agent('network-overview')"""
        def decorator(cls: Type[BaseAgent]):
            self.register_agent(name, cls)
            return cls
        return decorator

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    def list_handlers(self):
        return list(self._handlers.keys())

    def list_agents(self):
        return list(self._agents.keys())


# Global default registry
default_registry = Registry()
