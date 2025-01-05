from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BookmarkOutput(BaseModel):
    film_id: UUID
    created_at: datetime
