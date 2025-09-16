"""Data transformation logic for animal data."""

import logging
from typing import List

from .models import AnimalDetail, TransformedAnimal

logger = logging.getLogger(__name__)


class AnimalTransformer:
    """Handles transformation of animal data."""

    def transform_animal(self, animal_detail: AnimalDetail) -> TransformedAnimal:
        """Transform a single animal's data."""
        logger.debug(f"Transforming animal {animal_detail.id}: {animal_detail.name}")

        try:
            # The Pydantic validators will handle the transformation
            transformed = TransformedAnimal(
                id=animal_detail.id,
                name=animal_detail.name,
                born_at=animal_detail.born_at,  # type: ignore
                friends=animal_detail.friends,  # type: ignore
            )
            logger.debug(f"Successfully transformed animal {animal_detail.id}")
            return transformed
        except Exception as e:
            logger.error(f"Failed to transform animal {animal_detail.id}: {e}")
            raise

    def transform_animals_batch(
        self, animal_details: List[AnimalDetail]
    ) -> List[TransformedAnimal]:
        """Transform a batch of animal details."""
        logger.info(f"Transforming batch of {len(animal_details)} animals")

        transformed_animals = []
        errors = []

        for animal_detail in animal_details:
            try:
                transformed = self.transform_animal(animal_detail)
                transformed_animals.append(transformed)
            except Exception as e:
                logger.error(f"Failed to transform animal {animal_detail.id}: {e}")
                errors.append((animal_detail.id, str(e)))
                # Continue processing other animals
                continue

        if errors:
            logger.warning(f"Encountered {len(errors)} transformation errors")
            for animal_id, error in errors:
                logger.warning(f"Animal {animal_id}: {error}")

        logger.info(f"Successfully transformed {len(transformed_animals)} animals")
        return transformed_animals
