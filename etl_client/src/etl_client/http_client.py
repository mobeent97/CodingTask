"""HTTP client with retry logic for handling API chaos."""
import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)
from urllib3.util.retry import Retry

from .config import settings

logger = logging.getLogger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):
    """HTTP adapter with configurable timeout."""

    def __init__(self, timeout: int, *args, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        return super().send(request, **kwargs)


class AnimalAPIClient:
    """HTTP client for the Animals API with retry logic."""

    def __init__(self):
        self.base_url = settings.api_base_url.rstrip('/')
        self.timeout = settings.api_timeout

        # Configure retry strategy for urllib3
        retry_strategy = Retry(
            total=settings.api_max_retries,
            backoff_factor=settings.api_backoff_multiplier,
            status_forcelist=[500, 502, 503, 504],  # Server errors
            method_whitelist=["GET", "POST"],  # HTTP methods to retry
        )

        # Create session with retry adapter
        self.session = requests.Session()
        adapter = TimeoutHTTPAdapter(timeout=self.timeout)
        adapter.max_retries = retry_strategy
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(settings.api_max_retries),
        wait=wait_exponential(
            multiplier=settings.api_retry_delay,
            max=settings.api_timeout
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making {method} request to {url}")

        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_animals_page(self, page: int = 1) -> Dict[str, Any]:
        """Get a page of animals from the API."""
        endpoint = f"/animals/v1/animals?page={page}"
        response = self._make_request("GET", endpoint)
        return response.json()

    def get_animal_details(self, animal_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific animal."""
        endpoint = f"/animals/v1/animals/{animal_id}"
        response = self._make_request("GET", endpoint)
        return response.json()

    def post_animals_home(self, animals: list) -> Dict[str, Any]:
        """Post a batch of animals to the home endpoint."""
        endpoint = "/animals/v1/home"
        response = self._make_request(
            "POST",
            endpoint,
            json=animals,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
