from datetime import datetime, UTC
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from ugc_service.src.core.settings import app_settings


class Bookmark(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    film_id: UUID
    created_at: datetime
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_deleted: bool = Field(default=False)

    class Settings:
        name = app_settings.bookmark_collection
