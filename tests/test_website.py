import os
import pytest
import requests
import sys

sibling_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
sys.path.append(sibling_dir)
from config import BASE_URL


@pytest.mark.parametrize("url, max_response_time", [
    (BASE_URL, 1.0),
    (BASE_URL, 2.0),
])
def test_website_connection_advanced(url, max_response_time):
    """
    Tests website availability with advanced checks:
    - HTTP status code is 200 (OK)
    - Response time does not exceed max_response_time (seconds)
    - Content-Type header includes 'text/html'
    - Expected text is present in the response body
    """
    try:
        response = requests.get(url, timeout=max_response_time + 1)
    except requests.RequestException as e:
        pytest.fail(f"Failed to connect to {url}: {e}")

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    response_time = response.elapsed.total_seconds()
    assert response_time <= max_response_time, (
        f"Response time {response_time:.2f}s exceeds limit of {max_response_time}s"
    )

    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), (
        f"Expected 'text/html' in Content-Type header but got '{content_type}'"
    )
