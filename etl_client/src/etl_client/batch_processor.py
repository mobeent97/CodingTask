from .models import AnimalDetail, TransformedAnimal
from .transformer import AnimalTransformer
from .http_client import AnimalAPIClient
from typing import List, Optional
import logging, queue, threading
from .config import settings
from tqdm import tqdm


logger = logging.getLogger(__name__)


class BatchProcessor:

    def __init__(self, http_client: AnimalAPIClient, transformer: AnimalTransformer):
        self.http_client = http_client
        self.transformer = transformer
        self.batch_size = settings.batch_size
        self.max_workers = settings.max_workers

    def process_animals(self, animal_ids: List[int]) -> None:
        logger.info(f"Starting concurrent ETL processing for {len(animal_ids)} animals")
        work_queue = queue.Queue()
        total_animals = len(animal_ids)
        logger.info(f"Distributing {total_animals} animals across workers in batches of {self.batch_size}")

        for i in range(0, len(animal_ids), self.batch_size):
            batch_ids = animal_ids[i : i + self.batch_size]
            work_queue.put((i // self.batch_size + 1, batch_ids))

        for _ in range(self.max_workers):
            work_queue.put(None)

        total_batches = (len(animal_ids) + self.batch_size - 1) // self.batch_size
        logger.info(f"Created {total_batches} batches to be processed by {self.max_workers} workers")
        completed_batches = 0
        progress_lock = threading.Lock()

        def etl_worker(worker_id: int):
            nonlocal completed_batches

            while True:
                batch_info = work_queue.get()
                if batch_info is None:  # Sentinel value
                    break
                batch_num, batch_ids = batch_info
                logger.info(f"Worker {worker_id}: Processing batch {batch_num} with {len(batch_ids)} animals (IDs: {batch_ids[0]} to {batch_ids[-1]})")
                try:
                    animal_details = self._fetch_animal_details_sequentially(batch_ids)
                    transformed_animals = self.transformer.transform_animals_batch(animal_details)
                    if transformed_animals:
                        self._post_animals_batch(transformed_animals)
                        logger.info(f"Worker {worker_id}: Successfully processed and posted batch {batch_num} ({len(transformed_animals)} animals)")
                    else:
                        logger.warning(f"Worker {worker_id}: No animals to post in batch {batch_num} after transformation")
                    with progress_lock:
                        completed_batches += 1
                        logger.info(f"Progress: {completed_batches}/{total_batches} batches completed")
                except Exception as e:
                    logger.error(f"Worker {worker_id}: Failed to process batch {batch_num}: {e}")
                work_queue.task_done()

            logger.info(f"Worker {worker_id}: Finished processing all assigned batches")
        workers = []
        logger.info(f"Starting {self.max_workers} concurrent ETL worker threads")
        for worker_id in range(self.max_workers):
            worker_thread = threading.Thread(target=etl_worker, args=(worker_id + 1,))
            worker_thread.daemon = True
            worker_thread.start()
            logger.info(f"Worker thread {worker_id + 1} started")
            workers.append(worker_thread)
        work_queue.join()

        logger.info("Waiting for all worker threads to complete...")
        for i, worker in enumerate(workers, 1):
            worker.join()
            logger.info(f"Worker thread {i} has completed")

        logger.info(f"Concurrent ETL processing completed successfully: {total_animals} animals processed in {total_batches} batches using {self.max_workers} workers")


    def _fetch_animal_details_sequentially(self, animal_ids: List[int]) -> List[AnimalDetail]:
        logger.debug(f"Fetching details for {len(animal_ids)} animals sequentially")
        animal_details = []
        for animal_id in tqdm(
            animal_ids,
            desc="Fetching animal details",
            unit="animal",
        ):
            try:
                animal_detail = self._fetch_single_animal(animal_id)
                if animal_detail:
                    animal_details.append(animal_detail)
            except Exception as e:
                logger.error(f"Failed to fetch animal {animal_id}: {e}")
                continue
        logger.debug(f"Successfully fetched {len(animal_details)} animal details")
        return animal_details


    def _fetch_single_animal(self, animal_id: int) -> Optional[AnimalDetail]:
        try:
            response_data = self.http_client.get_animal_details(animal_id)
            return AnimalDetail(**response_data)
        except Exception as e:
            logger.error(f"Failed to fetch animal {animal_id}: {e}")
            return None


    def _post_animals_batch(self, transformed_animals: List[TransformedAnimal]) -> None:
        try:
            if len(transformed_animals) > 100:
                logger.error(
                f"Batch size {len(transformed_animals)} exceeds maximum of 100"
                )
                raise ValueError("Batch size cannot exceed 100 animals")
            logger.debug(
                f"Posting batch of {len(transformed_animals)} animals to home endpoint"
            )
            animals_dict = [animal.dict() for animal in transformed_animals]
            response = self.http_client.post_animals_home(animals_dict)
            logger.info(
                f"Successfully posted batch: {response.get('message', 'No message')}"
            )
        except Exception as e:
            logger.error(f"Failed to post animals batch: {e}")
            raise
