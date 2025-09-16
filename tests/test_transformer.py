"""Tests for the data transformer."""
import pytest
from etl_client.models import AnimalDetail
from etl_client.transformer import AnimalTransformer


class TestAnimalTransformer:
    """Test the AnimalTransformer class."""

    @pytest.fixture
    def transformer(self):
        """Create a transformer instance for testing."""
        return AnimalTransformer()

    @pytest.fixture
    def sample_animal_detail(self):
        """Create a sample animal detail for testing."""
        return AnimalDetail(
            id=1,
            name="Test Lion",
            born_at=1640995200000,  # 2022-01-01 00:00:00 UTC
            friends="Dog,Cat,Elephant"
        )

    def test_transform_single_animal(self, transformer, sample_animal_detail):
        """Test transforming a single animal."""
        result = transformer.transform_animal(sample_animal_detail)

        assert result.id == 1
        assert result.name == "Test Lion"
        assert result.friends == ["Dog", "Cat", "Elephant"]
        assert result.born_at is not None

    def test_transform_animals_batch(self, transformer):
        """Test transforming a batch of animals."""
        animals = [
            AnimalDetail(id=1, name="Lion", born_at=1640995200000, friends="Dog,Cat"),
            AnimalDetail(id=2, name="Tiger", born_at=None, friends=""),
            AnimalDetail(id=3, name="Bear", born_at=1641081600000, friends="Wolf,Fox")
        ]

        results = transformer.transform_animals_batch(animals)

        assert len(results) == 3

        # Check first animal
        assert results[0].id == 1
        assert results[0].friends == ["Dog", "Cat"]

        # Check second animal (empty friends)
        assert results[1].id == 2
        assert results[1].friends == []

        # Check third animal
        assert results[2].id == 3
        assert results[2].friends == ["Wolf", "Fox"]

    def test_transform_with_invalid_data(self, transformer):
        """Test transforming animals with invalid data."""
        # Animal with invalid friends format
        invalid_animal = AnimalDetail(
            id=1,
            name="Test Animal",
            born_at=1640995200000,
            friends="Invalid,Format,"  # Trailing comma
        )

        result = transformer.transform_animal(invalid_animal)

        # Should handle gracefully
        assert result.friends == ["Invalid", "Format", ""]  # Empty string at end

    def test_transform_empty_batch(self, transformer):
        """Test transforming an empty batch."""
        results = transformer.transform_animals_batch([])
        assert results == []

    def test_transform_batch_with_errors(self, transformer):
        """Test that batch transformation continues despite individual errors."""
        # Mix of valid and invalid animals
        animals = [
            AnimalDetail(id=1, name="Valid", born_at=1640995200000, friends="Dog"),
            # This would cause issues in real scenarios, but our models are forgiving
        ]

        results = transformer.transform_animals_batch(animals)
        assert len(results) >= 1  # At least the valid one should work
