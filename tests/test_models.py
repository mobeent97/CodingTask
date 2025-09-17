"""Tests for data models and transformations."""
import pytest
from datetime import datetime
from etl_client.models import AnimalDetail, TransformedAnimal


class TestAnimalModels:
    """Test animal data models and transformations."""

    def test_animal_detail_creation(self):
        """Test creating an AnimalDetail instance."""
        animal = AnimalDetail(
            id=1,
            name="Test Animal",
            born_at=1640995200000,  # 2022-01-01 00:00:00 UTC in milliseconds
            friends=["Dog", "Cat", "Bird"]
        )

        assert animal.id == 1
        assert animal.name == "Test Animal"
        assert animal.born_at == 1640995200000
        assert animal.friends == ["Dog", "Cat", "Bird"]

    def test_transformed_animal_friends_transformation(self):
        """Test that friends string is transformed to array."""
        animal = TransformedAnimal(
            id=1,
            name="Test Animal",
            born_at=None,
            friends="Dog,Cat,Bird"
        )

        assert animal.friends == ["Dog", "Cat", "Bird"]

    def test_transformed_animal_empty_friends(self):
        """Test handling of empty friends string."""
        animal = TransformedAnimal(
            id=1,
            name="Test Animal",
            born_at=None,
            friends=""
        )

        assert animal.friends == []

    def test_transformed_animal_born_at_transformation(self):
        """Test that born_at timestamp is transformed to ISO8601 string."""
        # 2022-01-01 00:00:00 UTC in milliseconds
        timestamp_ms = 1640995200000

        animal = TransformedAnimal(
            id=1,
            name="Test Animal",
            born_at=timestamp_ms,
            friends="Dog"
        )

        expected_iso_string = datetime.fromtimestamp(timestamp_ms / 1000).isoformat()
        assert animal.born_at == expected_iso_string
        assert isinstance(animal.born_at, str)

    def test_transformed_animal_none_born_at(self):
        """Test handling of None born_at value."""
        animal = TransformedAnimal(
            id=1,
            name="Test Animal",
            born_at=None,
            friends="Dog"
        )

        assert animal.born_at is None


class TestDataValidation:
    """Test data validation in models."""

    def test_invalid_id_type(self):
        """Test that invalid ID types raise validation errors."""
        with pytest.raises(Exception):  # Pydantic validation error
            AnimalDetail(
                id="invalid",
                name="Test Animal",
                born_at=1640995200000,
                friends=["Dog"]
            )

    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(Exception):  # Pydantic validation error
            AnimalDetail(
                id=1,
                # Missing name
                born_at=1640995200000,
                friends=["Dog"]
            )
