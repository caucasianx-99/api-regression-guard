# API Regression Guard

OpenAPI-driven API regression checks for local development and CI.

## v0.2 capability

- Load OpenAPI 3.x YAML/JSON
- Extract endpoints and expected response codes
- Safely call GET/HEAD endpoints that do not need path parameters
- Skip POST/PUT/PATCH/DELETE by default
- Skip templated paths like `/users/{id}`
- Return exit code `1` when a checked endpoint fails
- Include pytest coverage

## Install

```bash
python -m pip install -e ".[dev]"
```

## Inspect a spec

```bash
arguard inspect --spec examples/openapi.yaml
```

## Run safe checks against a real public demo API

```bash
arguard test --spec examples/openapi.yaml --base-url https://jsonplaceholder.typicode.com
```

Expected shape:

```text
PASS GET     /posts status=200
SKIP POST    /posts (unsafe or requires path parameters)
SKIP GET     /posts/{id} (unsafe or requires path parameters)
PASS GET     /users status=200

passed=2 failed=0 skipped=2
```

The tool deliberately avoids state-changing methods at this stage.
