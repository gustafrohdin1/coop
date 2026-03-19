"""
manifest.py — Agent manifest loading and validation.

A manifest is a JSON file that describes an agent:
  id, version, title, script, input_schema, output_schema, constraints
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


REQUIRED_FIELDS = ["id", "version", "title"]


class ManifestError(ValueError):
    pass


class Manifest:
    def __init__(self, data: Dict[str, Any], base_dir: Optional[Path] = None):
        self._data = data
        self.base_dir = base_dir or Path(".")
        self._validate()

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def version(self) -> str:
        return self._data["version"]

    @property
    def title(self) -> str:
        return self._data["title"]

    @property
    def description(self) -> str:
        return self._data.get("description", "")

    @property
    def script(self) -> Optional[Path]:
        s = self._data.get("script")
        return self.base_dir / s if s else None

    @property
    def input_schema(self) -> Dict[str, Any]:
        return self._data.get("input_schema", {})

    @property
    def output_schema(self) -> Dict[str, Any]:
        return self._data.get("output_schema", {})

    @property
    def constraints(self) -> Dict[str, Any]:
        return self._data.get("constraints", {})

    @property
    def timeout(self) -> Optional[int]:
        return self.constraints.get("timeout")

    @property
    def requires_admin(self) -> bool:
        return self.constraints.get("requires_admin", False)

    @property
    def network_allowed(self) -> bool:
        return self.constraints.get("network_allowed", True)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Manifest":
        path = Path(path)
        with open(path) as f:
            data = json.load(f)
        return cls(data, base_dir=path.parent)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self):
        for field in REQUIRED_FIELDS:
            if field not in self._data:
                raise ManifestError(f"Missing required field: {field}")

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input against input_schema. Extend for full jsonschema support."""
        if not self.input_schema:
            return True
        # TODO: plug in jsonschema here when needed
        return True
