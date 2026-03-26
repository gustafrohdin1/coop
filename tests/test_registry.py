"""
test_registry.py — Test Registry handler/agent registration and lookup.
"""

import pytest
from src.coop.sdk.registry import Registry, default_registry
from src.coop.sdk.handler import BaseHandler
from src.coop.sdk.agent import BaseAgent
from src.coop.manifest import Manifest
from src.coop.events import Event


MINIMAL_MANIFEST = {"id": "reg-agent", "version": "1.0.0", "title": "Reg Agent"}


class ConcreteHandler(BaseHandler):
    def on_event(self, event: Event):
        pass


class AnotherHandler(BaseHandler):
    def on_event(self, event: Event):
        pass


class ConcreteAgent(BaseAgent):
    def execute(self, input_data):
        return 0


class AnotherAgent(BaseAgent):
    def execute(self, input_data):
        return 0


# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------

def test_register_and_get_handler():
    r = Registry()
    r.register_handler("my-handler", ConcreteHandler)
    assert r.get_handler("my-handler") is ConcreteHandler


def test_get_unknown_handler_raises():
    r = Registry()
    with pytest.raises(KeyError, match="No handler registered"):
        r.get_handler("nope")


def test_get_unknown_handler_error_lists_available():
    r = Registry()
    r.register_handler("terminal", ConcreteHandler)
    with pytest.raises(KeyError, match="terminal"):
        r.get_handler("missing")


def test_handler_decorator_registers_class():
    r = Registry()

    @r.handler("decorated")
    class MyHandler(BaseHandler):
        def on_event(self, event: Event):
            pass

    assert r.get_handler("decorated") is MyHandler


def test_handler_decorator_returns_class_unchanged():
    r = Registry()

    @r.handler("passthrough")
    class MyHandler(BaseHandler):
        def on_event(self, event: Event):
            pass

    assert MyHandler.__name__ == "MyHandler"


def test_register_handler_overwrites():
    r = Registry()
    r.register_handler("h", ConcreteHandler)
    r.register_handler("h", AnotherHandler)
    assert r.get_handler("h") is AnotherHandler


def test_list_handlers_empty():
    r = Registry()
    assert r.list_handlers() == []


def test_list_handlers_returns_names():
    r = Registry()
    r.register_handler("alpha", ConcreteHandler)
    r.register_handler("beta", AnotherHandler)
    names = r.list_handlers()
    assert "alpha" in names
    assert "beta" in names


# ------------------------------------------------------------------
# Agents
# ------------------------------------------------------------------

def test_register_and_get_agent():
    r = Registry()
    r.register_agent("my-agent", ConcreteAgent)
    assert r.get_agent("my-agent") is ConcreteAgent


def test_get_unknown_agent_raises():
    r = Registry()
    with pytest.raises(KeyError, match="No agent registered"):
        r.get_agent("nope")


def test_get_unknown_agent_error_lists_available():
    r = Registry()
    r.register_agent("known", ConcreteAgent)
    with pytest.raises(KeyError, match="known"):
        r.get_agent("missing")


def test_agent_decorator_registers_class():
    r = Registry()

    @r.agent("my-decorated-agent")
    class MyAgent(BaseAgent):
        def execute(self, input_data):
            return 0

    assert r.get_agent("my-decorated-agent") is MyAgent


def test_agent_decorator_returns_class_unchanged():
    r = Registry()

    @r.agent("passthrough-agent")
    class MyAgent(BaseAgent):
        def execute(self, input_data):
            return 0

    assert MyAgent.__name__ == "MyAgent"


def test_register_agent_overwrites():
    r = Registry()
    r.register_agent("a", ConcreteAgent)
    r.register_agent("a", AnotherAgent)
    assert r.get_agent("a") is AnotherAgent


def test_list_agents_empty():
    r = Registry()
    assert r.list_agents() == []


def test_list_agents_returns_names():
    r = Registry()
    r.register_agent("x", ConcreteAgent)
    r.register_agent("y", AnotherAgent)
    names = r.list_agents()
    assert "x" in names
    assert "y" in names


# ------------------------------------------------------------------
# Handlers and agents are independent namespaces
# ------------------------------------------------------------------

def test_handler_and_agent_registries_are_independent():
    r = Registry()
    r.register_handler("shared-name", ConcreteHandler)
    r.register_agent("shared-name", ConcreteAgent)
    assert r.get_handler("shared-name") is ConcreteHandler
    assert r.get_agent("shared-name") is ConcreteAgent


# ------------------------------------------------------------------
# default_registry
# ------------------------------------------------------------------

def test_default_registry_is_registry_instance():
    assert isinstance(default_registry, Registry)
