"""
test_manifest.py — Test manifest loading and validation.
"""

import pytest
from src.coop.manifest import Manifest, ManifestError


VALID = {
    "id": "test-agent",
    "version": "1.0.0",
    "title": "Test Agent",
    "description": "A test agent",
    "script": "test.sh",
    "constraints": {"timeout": 30, "requires_admin": False, "network_allowed": True},
}


def test_valid_manifest():
    m = Manifest(VALID)
    assert m.id == "test-agent"
    assert m.version == "1.0.0"
    assert m.title == "Test Agent"
    assert m.timeout == 30
    assert m.requires_admin is False
    assert m.network_allowed is True


def test_missing_required_field():
    bad = {k: v for k, v in VALID.items() if k != "id"}
    with pytest.raises(ManifestError, match="Missing required field: id"):
        Manifest(bad)


def test_missing_version():
    bad = {k: v for k, v in VALID.items() if k != "version"}
    with pytest.raises(ManifestError):
        Manifest(bad)


def test_optional_fields_have_defaults():
    minimal = {"id": "x", "version": "1.0.0", "title": "X"}
    m = Manifest(minimal)
    assert m.description == ""
    assert m.script is None
    assert m.input_schema == {}
    assert m.constraints == {}
    assert m.timeout is None
