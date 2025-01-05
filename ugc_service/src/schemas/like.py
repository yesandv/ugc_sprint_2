from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LikeInput(BaseModel):
    film_id: UUID
    rating: int = Field(ge=0, le=10)


class LikeOutput(BaseModel):
    film_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime
