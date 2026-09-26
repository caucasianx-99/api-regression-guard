import httpx

from api_regression_guard.models import Endpoint
from api_regression_guard.runner import is_safe_to_run, run_endpoint

def test_safe_get_passes():
    endpoint = Endpoint("GET", "/health", None, (200,))

    def handler(request: httpx.Request):
        return httpx.Response(200, json={"ok": True})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = run_endpoint(client, "https://example.test", endpoint)
    client.close()

    assert result.status == "PASS"
    assert result.actual_status == 200

def test_wrong_status_fails():
    endpoint = Endpoint("GET", "/health", None, (200,))

    def handler(request: httpx.Request):
        return httpx.Response(500, json={"error": "boom"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = run_endpoint(client, "https://example.test", endpoint)
    client.close()

    assert result.status == "FAIL"
    assert result.actual_status == 500

def test_post_is_skipped():
    endpoint = Endpoint("POST", "/users", None, (201,))
    assert not is_safe_to_run(endpoint)

def test_path_parameter_is_skipped():
    endpoint = Endpoint("GET", "/users/{id}", None, (200,))
    assert not is_safe_to_run(endpoint)
