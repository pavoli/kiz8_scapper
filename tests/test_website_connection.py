import os
import pytest
import requests
import sys

sibling_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
sys.path.append(sibling_dir)
from config import BASE_URL


def test_website_connection():
    try:
        response = requests.get(BASE_URL, timeout=5)
        assert response.status_code == 200
    except requests.RequestException as e:
        pytest.fail(f"Connection to {BASE_URL} failed: {e}")
