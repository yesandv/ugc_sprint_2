from uuid import UUID

from pydantic import BaseModel, Field


class ReviewInput(BaseModel):
    film_id: UUID
    text: str = Field(max_length=5000)


class ReviewOutput(BaseModel):
    user_id: UUID
    film_id: UUID
    text: str = Field(max_length=5000)
    score: int | None = None
