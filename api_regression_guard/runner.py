from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from .models import Endpoint

SAFE_METHODS = {"GET", "HEAD"}

@dataclass(frozen=True)
class CheckResult:
    endpoint: Endpoint
    status: str
    actual_status: int | None = None
    message: str | None = None

def _expected_success_statuses(endpoint: Endpoint) -> set[int]:
    success = {code for code in endpoint.expected_statuses if 200 <= code < 300}
    return success or {200}

def is_safe_to_run(endpoint: Endpoint) -> bool:
    return endpoint.method in SAFE_METHODS and "{" not in endpoint.path and "}" not in endpoint.path

def run_endpoint(
    client: httpx.Client,
    base_url: str,
    endpoint: Endpoint,
) -> CheckResult:
    if not is_safe_to_run(endpoint):
        return CheckResult(endpoint=endpoint, status="SKIP", message="unsafe or requires path parameters")

    url = urljoin(base_url.rstrip("/") + "/", endpoint.path.lstrip("/"))
    expected = _expected_success_statuses(endpoint)

    try:
        response = client.request(endpoint.method, url)
    except httpx.TimeoutException:
        return CheckResult(endpoint=endpoint, status="FAIL", message="timeout")
    except httpx.HTTPError as exc:
        return CheckResult(endpoint=endpoint, status="FAIL", message=str(exc))

    if response.status_code in expected:
        return CheckResult(
            endpoint=endpoint,
            status="PASS",
            actual_status=response.status_code,
        )

    exp = ",".join(str(code) for code in sorted(expected))
    return CheckResult(
        endpoint=endpoint,
        status="FAIL",
        actual_status=response.status_code,
        message=f"expected one of [{exp}]",
    )

def run_checks(
    base_url: str,
    endpoints: list[Endpoint],
    timeout: float = 10.0,
) -> list[CheckResult]:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        return [run_endpoint(client, base_url, endpoint) for endpoint in endpoints]
