"""Pagination handler for fetching all animals from the API."""

import logging
from typing import List

from tqdm import tqdm

from .http_client import AnimalAPIClient
from .models import AnimalsPage

logger = logging.getLogger(__name__)


class PaginationHandler:
    """Handles pagination for fetching all animals from the API."""

    def __init__(self, http_client: AnimalAPIClient):
        self.http_client = http_client

    def get_all_animal_ids(self) -> List[int]:
        """Fetch all animal IDs by paginating through the animals listing."""
        logger.info("Starting to fetch all animal IDs")

        all_animal_ids = []
        page = 1
        total_pages = None

        with tqdm(desc="Fetching animal pages", unit="page") as pbar:
            while total_pages is None or page <= total_pages:
                try:
                    page_data = self._fetch_animals_page(page)
                    animal_ids = [animal.id for animal in page_data.items]

                    all_animal_ids.extend(animal_ids)
                    logger.debug(
                        f"Fetched page {page}/{page_data.total_pages} with {len(animal_ids)} animals"
                    )

                    if total_pages is None:
                        total_pages = page_data.total_pages
                        pbar.total = total_pages
                        logger.info(f"Total pages to fetch: {total_pages}")

                    pbar.update(1)
                    page += 1

                except Exception as e:
                    logger.error(f"Failed to fetch page {page}: {e}")
                    # Continue with next page - the HTTP client has retry logic
                    pbar.update(1)
                    page += 1
                    continue

        logger.info(
            f"Successfully fetched {len(all_animal_ids)} animal IDs from {total_pages} pages"
        )
        return all_animal_ids

    def _fetch_animals_page(self, page: int) -> AnimalsPage:
        """Fetch a single page of animals."""
        response_data = self.http_client.get_animals_page(page)
        return AnimalsPage(**response_data)
