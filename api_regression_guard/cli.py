from __future__ import annotations

import argparse
import sys

from .parser import SpecError, extract_endpoints, load_spec
from .runner import run_checks

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arguard",
        description="OpenAPI-driven API regression checks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_cmd = sub.add_parser("inspect", help="List endpoints in an OpenAPI file.")
    inspect_cmd.add_argument("--spec", required=True, help="Path to OpenAPI YAML/JSON file.")

    test_cmd = sub.add_parser(
        "test",
        help="Safely test GET/HEAD endpoints without path parameters.",
    )
    test_cmd.add_argument("--spec", required=True, help="Path to OpenAPI YAML/JSON file.")
    test_cmd.add_argument("--base-url", required=True, help="Base URL of the API.")
    test_cmd.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds.")

    return parser

def _load_endpoints(spec_path: str):
    spec = load_spec(spec_path)
    return spec, extract_endpoints(spec)

def run_inspect(spec_path: str) -> int:
    try:
        spec, endpoints = _load_endpoints(spec_path)
    except SpecError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("API Regression Guard")
    print(f"OpenAPI: {spec.get('openapi')}")
    print(f"Endpoints: {len(endpoints)}")
    print()

    for endpoint in endpoints:
        statuses = ",".join(map(str, endpoint.expected_statuses)) if endpoint.expected_statuses else "-"
        summary = f" — {endpoint.summary}" if endpoint.summary else ""
        print(f"{endpoint.method:<7} {endpoint.path:<30} expected=[{statuses}]{summary}")

    return 0

def run_test(spec_path: str, base_url: str, timeout: float) -> int:
    try:
        _, endpoints = _load_endpoints(spec_path)
    except SpecError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    results = run_checks(base_url, endpoints, timeout=timeout)

    print("API Regression Guard")
    print(f"Base URL: {base_url}")
    print()

    passed = failed = skipped = 0

    for result in results:
        label = result.status
        actual = f" status={result.actual_status}" if result.actual_status is not None else ""
        message = f" ({result.message})" if result.message else ""
        print(f"{label:<4} {result.endpoint.method:<7} {result.endpoint.path}{actual}{message}")

        if result.status == "PASS":
            passed += 1
        elif result.status == "FAIL":
            failed += 1
        else:
            skipped += 1

    print()
    print(f"passed={passed} failed={failed} skipped={skipped}")

    return 1 if failed else 0

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "inspect":
        raise SystemExit(run_inspect(args.spec))
    if args.command == "test":
        raise SystemExit(run_test(args.spec, args.base_url, args.timeout))

    raise SystemExit(1)

if __name__ == "__main__":
    main()
