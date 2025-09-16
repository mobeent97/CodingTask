"""Shared test fixtures and configuration."""
import pytest
from unittest.mock import Mock

from etl_client.http_client import AnimalAPIClient


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    client = Mock(spec=AnimalAPIClient)

    # Configure mock responses
    client.get_animals_page.return_value = {
        "page": 1,
        "total_pages": 2,
        "items": [
            {"id": 1, "name": "Lion", "born_at": 1640995200000},
            {"id": 2, "name": "Tiger", "born_at": None}
        ]
    }

    client.get_animal_details.return_value = {
        "id": 1,
        "name": "Lion",
        "born_at": 1640995200000,
        "friends": "Tiger,Elephant"
    }

    client.post_animals_home.return_value = {
        "message": "Helped 2 animals find home"
    }

    return client
