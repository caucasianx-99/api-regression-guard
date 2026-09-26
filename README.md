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