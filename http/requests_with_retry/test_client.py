import pytest
import requests
from http_client import HttpClient


@pytest.fixture
def http_client():
    client = HttpClient(try_count=3, default_timeout_sec=15, retry_wait_interval_sec=0.5)
    return client


def test_setting_headers():
    # Get request to this url returns request headers in body of response
    url = "https://httpbin.org/headers"
    default_content_type = 'default_type'
    http_client = HttpClient(try_count=1,
                             default_headers={'Content-Type': default_content_type})
    r = http_client.get(url)
    assert r.json()['headers']['Content-Type'] == default_content_type

    overridden_content_type = 'my_content_type'
    r = http_client.get(url, headers={'Content-Type': overridden_content_type}, timeout=2)
    assert r.json()['headers']['Content-Type'] == overridden_content_type


def test_negative_connection_error(http_client):
    url = "http://fkdjkjf"
    print(f"type(http_client) = {type(http_client)}")
    with pytest.raises(requests.exceptions.ConnectionError):
        http_client.get(url=url)


def test_negative_404(http_client):
    # Get request to this url returns 404
    url = "https://httpbin.org/hidden-basic-auth/:user/:passwd"
    with pytest.raises(requests.exceptions.HTTPError) as e:
        http_client.get(url=url)
    assert e.value.response.status_code == 404


@pytest.mark.parametrize(
    'response_status, description',
    [
     (requests.codes.ok, "OK (200), no retries"),
     (requests.codes.accepted, "ACCEPTED (202), no retries"),
     (requests.codes.no_content, "NO_CONTENT (204), no retries")
    ]
)
def test_response_status_success(http_client, response_status, description):
    """Should be no retries, result: success
    """
    # Returns given HTTP Status code
    url = f"https://httpbin.org/status/{response_status}"
    try:
        r = http_client.get(url=url)
        print(f"response: {r}")
    except Exception as e:
        assert False, f"GET request to {url}, failed with exception: '{e}', test description: '{description}'"


@pytest.mark.parametrize(
    'response_status, description',
    [
     (requests.codes.internal_server_error, "INTERNAL_SERVER_ERROR (500), retries should've been made"),
     (requests.codes.service_unavailable, "SERVICE_UNAVAILABLE (503), retries should've been made"),
     (requests.codes.gateway_timeout, "GATEWAY_TIMEOUT (507), insufficient storage")
    ]
)
def test_response_status_failure_with_retries(http_client, response_status, description):
    """Should be no retries, result: success
    Don't know how to check if retries were made
    """
    # Returns given HTTP Status code
    print(f"INPUT: response_status = {response_status}")
    url = f"https://httpbin.org/status/{response_status}"
    with pytest.raises(requests.HTTPError) as e:
        http_client.get(url=url)
    # Uncomment if you want to test output to make sure retries are made:
    if e:
        print(f"GET {url}: e = {e}")
        print(f"GET {url}: type(e) = {type(e)}")
        print(f"GET {url}: dir(e) = {dir(e)}")
        print(f"GET {url}: e.value = {e.value}")
        assert False, f"GET request to {url}, failed with exception: '{e}', test description: '{description}'"


@pytest.mark.parametrize(
    'response_status, description',
    [
     (requests.codes.bad_request, "BAD_REQUEST (400), retries shouldn't have been made"),
     (requests.codes.unauthorized, "UNAUTHORIZED (401), retries shouldn't have been made"),
     (requests.codes.not_found, "NOT_FOUND (404), retries shouldn't have been made"),
     (requests.codes.method_not_allowed, "METHOD_NOT_ALLOWED (405), retries shouldn't have been made"),
    ]
)
def test_response_status_failure_without_retries(http_client, response_status, description):
    """Should be no retries, result: success
    Don't know how to check if retries were made
    """
    # Returns given HTTP Status code
    print(f"INPUT: response_status = {response_status}")
    url = f"https://httpbin.org/status/{response_status}"
    with pytest.raises(requests.HTTPError) as e:
        http_client.get(url=url)
    # Uncomment if you want to test output to make sure retries aren't made:
    # if e:
    #     assert False, f"GET request to {url}, failed with exception: '{e}', test description: '{description}'"


def test_post_positive(http_client):
    # Returns POST data
    url = "https://httpbin.org/post"
    data = "Hello"
    r = http_client.post(url=url, data=data)
    assert r.json()['data'] == data
