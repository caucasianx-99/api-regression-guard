from pathlib import Path
import pytest

from api_regression_guard.parser import SpecError, extract_endpoints, load_spec

def test_extracts_endpoints_from_yaml(tmp_path: Path):
    p = tmp_path / "openapi.yaml"
    p.write_text("""
openapi: 3.0.3
info:
  title: Demo
  version: "1.0"
paths:
  /health:
    get:
      summary: Health check
      responses:
        "200":
          description: OK
  /users:
    post:
      responses:
        "201":
          description: Created
        "400":
          description: Bad request
""", encoding="utf-8")

    endpoints = extract_endpoints(load_spec(p))

    assert [(e.method, e.path) for e in endpoints] == [
        ("GET", "/health"),
        ("POST", "/users"),
    ]
    assert endpoints[0].expected_statuses == (200,)
    assert endpoints[1].expected_statuses == (201, 400)

def test_rejects_missing_openapi_field(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("paths: {}", encoding="utf-8")

    with pytest.raises(SpecError, match="openapi"):
        load_spec(p)

def test_rejects_missing_file():
    with pytest.raises(SpecError, match="not found"):
        load_spec("does-not-exist.yaml")
