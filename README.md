# API Regression Guard

Catch API regressions from your OpenAPI specification before they reach production.

API Regression Guard is a lightweight Python CLI that checks a live API against the response status codes defined in an OpenAPI specification.

It is designed for local development and CI/CD workflows.

## Why?

An API can change unexpectedly after a deployment:

- an endpoint that returned `200` starts returning `500`
- a route disappears
- a documented response no longer matches the running service
- a deployment introduces a regression that manual testing misses

API Regression Guard turns these checks into a simple command that can also fail your CI pipeline automatically.

## Quick example

```bash
arguard test \
  --spec examples/openapi.yaml \
  --base-url https://your-api.example.com
  ```

Example output:

```text
API Regression Guard
Base URL: https://your-api.example.com

PASS GET     /posts status=200
SKIP POST    /posts (unsafe or requires path parameters)
SKIP GET     /posts/{id} (unsafe or requires path parameters)
PASS GET     /users status=200

passed=2 failed=0 skipped=2
```

If the live API violates the expected response status:

```text
FAIL GET /users status=500 (expected one of [200])

passed=1 failed=1 skipped=2
```

The command exits with status code `1`, allowing CI/CD pipelines to fail automatically when a regression is detected.

## Current capabilities

API Regression Guard currently supports:

- OpenAPI 3.x YAML and JSON specifications
- automatic endpoint discovery
- documented HTTP response status checks
- live HTTP requests
- GET and HEAD endpoints
- request timeouts and network error handling
- CI-friendly exit codes
- GitHub Actions integration
- automated pytest coverage

For safety, the current version skips:

- POST
- PUT
- PATCH
- DELETE
- endpoints requiring path parameters such as `/users/{id}`

This prevents the tool from unintentionally modifying API data.

## Installation

Requires Python 3.10+.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install the project:

```bash
python -m pip install git+https://github.com/caucasianx-99/api-regression-guard.git
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
```

## Inspect an OpenAPI specification

```bash
arguard inspect --spec examples/openapi.yaml
```

## GitHub Actions

API Regression Guard can run automatically on every push.

```yaml
name: API Regression Check

on:
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  regression:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

        - name: Install API Regression Guard
          run: python -m pip install git+https://github.com/caucasianx-99/api-regression-guard.git

      - name: Test API
        run: |
          arguard test \
            --spec examples/openapi.yaml \
            --base-url https://your-api.example.com
```

If a regression is detected, the command returns a non-zero exit code and the workflow fails.

## Run the test suite

```bash
pytest -q
```

## Project status

This project is currently an early prototype.

The current version intentionally focuses on:

1. reading an OpenAPI contract
2. discovering endpoints
3. safely calling non-destructive routes
4. detecting response-status regressions
5. working reliably inside CI

It does not currently provide a hosted dashboard, scheduled monitoring, historical reports, alerts, or team features.

Those capabilities will only be considered based on real developer usage and feedback.

## Possible future directions

- response schema validation
- authenticated API requests
- configurable path parameters
- safe request fixtures
- scheduled API checks
- regression history
- Slack/email alerts
- hosted monitoring
- team dashboards

## Feedback

If you try API Regression Guard on a real API, feedback is especially useful around:

- OpenAPI files that fail to parse
- regression cases the tool misses
- CI/CD integration problems
- features you currently maintain manually
- workflows where existing API testing tools feel too heavy

Please use GitHub Issues for reproducible bugs and feature requests.

## License

MIT