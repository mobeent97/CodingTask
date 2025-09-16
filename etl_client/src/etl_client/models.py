"""Data models for the Animal ETL pipeline."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class BaseAnimal(BaseModel):
    """Base animal model from API listing."""
    id: int
    name: str
    born_at: Optional[int]  # Unix timestamp in milliseconds


class AnimalDetail(BaseModel):
    """Detailed animal model from individual animal endpoint."""
    id: int
    name: str
    born_at: Optional[int]  # Unix timestamp in milliseconds
    friends: str  # Comma-delimited string


class TransformedAnimal(BaseModel):
    """Transformed animal model ready for POST to /home endpoint."""
    id: int
    name: str
    born_at: Optional[datetime]  # ISO8601 datetime in UTC
    friends: List[str]  # Array of friend names

    @validator('born_at', pre=True, always=True)
    def transform_born_at(cls, v):
        """Transform Unix timestamp to ISO8601 datetime."""
        if v is None:
            return None
        # Convert from milliseconds to seconds
        timestamp_seconds = v / 1000
        return datetime.fromtimestamp(timestamp_seconds)

    @validator('friends', pre=True, always=True)
    def transform_friends(cls, v):
        """Transform comma-delimited string to array."""
        if not v or v.strip() == "":
            return []
        return [friend.strip() for friend in v.split(',') if friend.strip()]


class AnimalsPage(BaseModel):
    """Response model for paginated animals listing."""
    items: List[BaseAnimal]
    page: int
    total_pages: int


class HomeResponse(BaseModel):
    """Response model for POST /home endpoint."""
    message: str
