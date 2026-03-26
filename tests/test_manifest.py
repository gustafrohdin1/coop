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


def test_load_from_file(tmp_path):
    import json
    data = {"id": "file-agent", "version": "2.0.0", "title": "File Agent", "script": "run.sh"}
    manifest_file = tmp_path / "agent.json"
    manifest_file.write_text(json.dumps(data))
    m = Manifest.load(manifest_file)
    assert m.id == "file-agent"
    assert m.version == "2.0.0"
    assert m.title == "File Agent"
    assert m.script == tmp_path / "run.sh"


def test_load_sets_base_dir(tmp_path):
    import json
    data = {"id": "bd-agent", "version": "1.0.0", "title": "BD"}
    f = tmp_path / "manifest.json"
    f.write_text(json.dumps(data))
    m = Manifest.load(f)
    assert m.base_dir == tmp_path


def test_script_resolved_against_base_dir(tmp_path):
    from pathlib import Path
    data = {"id": "s", "version": "1.0.0", "title": "S", "script": "sub/run.sh"}
    m = Manifest(data, base_dir=tmp_path)
    assert m.script == tmp_path / "sub" / "run.sh"


def test_validate_input_no_schema():
    m = Manifest({"id": "v", "version": "1.0.0", "title": "V"})
    assert m.validate_input({"anything": True}) is True


def test_validate_input_with_schema():
    data = {
        "id": "v", "version": "1.0.0", "title": "V",
        "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}}
    }
    m = Manifest(data)
    assert m.validate_input({"name": "alice"}) is True


def test_requires_admin_defaults_false():
    m = Manifest({"id": "a", "version": "1.0.0", "title": "A"})
    assert m.requires_admin is False


def test_network_allowed_defaults_true():
    m = Manifest({"id": "a", "version": "1.0.0", "title": "A"})
    assert m.network_allowed is True


def test_output_schema_default():
    m = Manifest({"id": "a", "version": "1.0.0", "title": "A"})
    assert m.output_schema == {}
