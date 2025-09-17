from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime


class BaseAnimal(BaseModel):
    """Base animal model from API listing."""

    id: int
    name: str
    born_at: Optional[int]  # Unix timestamp in milliseconds

    @validator("born_at", pre=True, always=True)
    def parse_born_at(cls, v) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return int(dt.timestamp() * 1000)
            except ValueError:
                try:
                    return int(float(v))
                except (ValueError, TypeError):
                    return None
        if isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        return None


class AnimalDetail(BaseModel):
    """Detailed animal model from individual animal endpoint."""

    id: int
    name: str
    born_at: Optional[int]
    friends: List[str]

    @validator("born_at", pre=True, always=True)
    def parse_born_at(cls, v) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return int(dt.timestamp() * 1000)
            except ValueError:
                try:
                    return int(float(v))
                except (ValueError, TypeError):
                    return None
        if isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        return None


class TransformedAnimal(BaseModel):
    """Transformed animal model ready for POST to /home endpoint."""

    id: int
    name: str
    born_at: Optional[str]  # ISO8601 timestamp string in UTC
    friends: List[str]

    @validator("born_at", pre=True, always=True)
    def transform_born_at(cls, v: Optional[int]) -> Optional[str]:
        """Transform Unix timestamp to ISO8601 timestamp string."""
        if v is None:
            return None
        timestamp_seconds = v / 1000
        dt = datetime.fromtimestamp(timestamp_seconds)
        return dt.isoformat()

    @validator("friends", pre=True, always=True)
    def transform_friends(cls, v) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if not v or v.strip() == "":
                return []
            return [friend.strip() for friend in v.split(",") if friend.strip()]
        return []


class AnimalsPage(BaseModel):
    """Response model for paginated animals listing."""

    items: List[BaseAnimal]
    page: int
    total_pages: int


class HomeResponse(BaseModel):
    """Response model for POST /home endpoint."""

    message: str
