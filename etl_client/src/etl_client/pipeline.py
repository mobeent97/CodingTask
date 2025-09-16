"""Main ETL pipeline orchestrator."""

import logging
import time
from typing import List

from .batch_processor import BatchProcessor
from .http_client import AnimalAPIClient
from .pagination import PaginationHandler
from .transformer import AnimalTransformer

logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL pipeline that orchestrates the entire animal processing workflow."""

    def __init__(self) -> None:
        """Initialize the ETL pipeline with all components."""
        self.http_client = AnimalAPIClient()
        self.pagination_handler = PaginationHandler(self.http_client)
        self.transformer = AnimalTransformer()
        self.batch_processor = BatchProcessor(self.http_client, self.transformer)

    def run(self) -> None:
        """Execute the complete ETL pipeline."""
        start_time = time.time()
        logger.info("Starting Animal ETL Pipeline")

        try:
            # Step 1: Extract - Get all animal IDs
            logger.info("Step 1: Extracting animal IDs")
            animal_ids = self._extract_animal_ids()
            if not animal_ids:
                logger.warning("No animals found to process")
                return

            # Step 2: Transform and Load - Process animals in batches
            logger.info("Step 2: Processing and loading animals")
            self._process_and_load_animals(animal_ids)

            # Success
            elapsed_time = time.time() - start_time
            logger.info(
                f"ETL Pipeline completed successfully in {elapsed_time:.2f} seconds"
            )
            logger.info("ETL Pipeline completed successfully")

        except KeyboardInterrupt:
            logger.info("ETL Pipeline interrupted by user")
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"ETL Pipeline failed after {elapsed_time:.2f} seconds: {e}")
            raise

    def _extract_animal_ids(self) -> List[int]:
        """Extract phase: Get all animal IDs from the API."""
        try:
            animal_ids = self.pagination_handler.get_all_animal_ids()
            logger.info(f"Extracted {len(animal_ids)} animal IDs")
            return animal_ids
        except Exception as e:
            logger.error(f"Failed during extraction phase: {e}")
            raise

    def _process_and_load_animals(self, animal_ids: List[int]) -> None:
        """Transform and Load phase: Process animals and send to home endpoint."""
        try:
            self.batch_processor.process_animals(animal_ids)
            logger.info("Transform and Load phase completed successfully")
        except Exception as e:
            logger.error(f"Failed during transform/load phase: {e}")
            raise
