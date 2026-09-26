from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .models import Endpoint

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}

class SpecError(ValueError):
    pass

def load_spec(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise SpecError(f"Spec file not found: {spec_path}")

    try:
        raw = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecError(f"Could not read spec file: {exc}") from exc

    try:
        data = json.loads(raw) if spec_path.suffix.lower() == ".json" else yaml.safe_load(raw)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SpecError(f"Invalid OpenAPI file: {exc}") from exc

    if not isinstance(data, dict):
        raise SpecError("OpenAPI document must be an object.")
    if "openapi" not in data:
        raise SpecError("Missing top-level 'openapi' field.")
    if not isinstance(data.get("paths"), dict):
        raise SpecError("Missing or invalid top-level 'paths' object.")

    return data

def _parse_statuses(responses: Any) -> tuple[int, ...]:
    if not isinstance(responses, dict):
        return ()

    statuses = []
    for key in responses:
        try:
            code = int(str(key))
        except ValueError:
            continue
        if 100 <= code <= 599:
            statuses.append(code)

    return tuple(sorted(set(statuses)))

def extract_endpoints(spec: dict[str, Any]) -> list[Endpoint]:
    endpoints: list[Endpoint] = []

    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            m = str(method).lower()
            if m not in HTTP_METHODS or not isinstance(operation, dict):
                continue

            summary = operation.get("summary")
            endpoints.append(
                Endpoint(
                    method=m.upper(),
                    path=str(path),
                    summary=str(summary) if summary is not None else None,
                    expected_statuses=_parse_statuses(operation.get("responses")),
                )
            )

    return sorted(endpoints, key=lambda e: (e.path, e.method))
