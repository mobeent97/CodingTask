"""Batch processor for fetching animal details and posting to home endpoint."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from tqdm import tqdm

from .config import settings
from .http_client import AnimalAPIClient
from .models import AnimalDetail, TransformedAnimal
from .transformer import AnimalTransformer

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handles batch processing of animal data."""

    def __init__(self, http_client: AnimalAPIClient, transformer: AnimalTransformer):
        self.http_client = http_client
        self.transformer = transformer
        self.batch_size = settings.batch_size
        self.max_workers = settings.max_workers

    def process_animals(self, animal_ids: List[int]) -> None:
        """Process all animals in batches."""
        logger.info(f"Starting to process {len(animal_ids)} animals")

        # Process in batches for memory efficiency
        for i in range(0, len(animal_ids), self.batch_size):
            batch_ids = animal_ids[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1} with {len(batch_ids)} animals")

            try:
                # Fetch details for this batch
                animal_details = self._fetch_animal_details_batch(batch_ids)

                # Transform the data
                transformed_animals = self.transformer.transform_animals_batch(animal_details)

                # Post to home endpoint
                if transformed_animals:
                    self._post_animals_batch(transformed_animals)
                else:
                    logger.warning("No animals to post in this batch")

            except Exception as e:
                logger.error(f"Failed to process batch starting at index {i}: {e}")
                # Continue with next batch
                continue

        logger.info("Completed processing all animal batches")

    def _fetch_animal_details_batch(self, animal_ids: List[int]) -> List[AnimalDetail]:
        """Fetch detailed information for a batch of animals using parallel requests."""
        logger.debug(f"Fetching details for {len(animal_ids)} animals")

        animal_details = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all requests
            future_to_id = {
                executor.submit(self._fetch_single_animal, animal_id): animal_id
                for animal_id in animal_ids
            }

            # Collect results as they complete
            for future in tqdm(
                as_completed(future_to_id),
                total=len(animal_ids),
                desc="Fetching animal details",
                unit="animal"
            ):
                animal_id = future_to_id[future]
                try:
                    animal_detail = future.result()
                    if animal_detail:
                        animal_details.append(animal_detail)
                except Exception as e:
                    logger.error(f"Failed to fetch animal {animal_id}: {e}")
                    # Continue processing other animals
                    continue

        logger.debug(f"Successfully fetched {len(animal_details)} animal details")
        return animal_details

    def _fetch_single_animal(self, animal_id: int) -> Optional[AnimalDetail]:
        """Fetch details for a single animal."""
        try:
            response_data = self.http_client.get_animal_details(animal_id)
            return AnimalDetail(**response_data)
        except Exception as e:
            logger.error(f"Failed to fetch animal {animal_id}: {e}")
            return None

    def _post_animals_batch(self, transformed_animals: List[TransformedAnimal]) -> None:
        """Post a batch of transformed animals to the home endpoint."""
        if len(transformed_animals) > 100:
            logger.error(f"Batch size {len(transformed_animals)} exceeds maximum of 100")
            raise ValueError("Batch size cannot exceed 100 animals")

        logger.debug(f"Posting batch of {len(transformed_animals)} animals to home endpoint")

        try:
            # Convert to dict for JSON serialization
            animals_dict = [animal.dict() for animal in transformed_animals]

            response = self.http_client.post_animals_home(animals_dict)
            logger.info(f"Successfully posted batch: {response.get('message', 'No message')}")

        except Exception as e:
            logger.error(f"Failed to post animals batch: {e}")
            raise
