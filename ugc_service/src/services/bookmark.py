from datetime import datetime, UTC
from uuid import UUID

from ugc_service.src.core.exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from ugc_service.src.models.bookmark import Bookmark


class BookmarkService:

    def __init__(self):
        self.model = Bookmark

    async def _get_one(self, user_id: str, film_id: UUID) -> Bookmark:
        return await self.model.find_one(
            self.model.user_id == UUID(user_id),
            self.model.film_id == film_id,
            self.model.is_deleted == False,  # noqa
        )

    async def create(self, user_id: str, film_id: UUID) -> UUID:
        bookmark = await self._get_one(user_id, film_id)
        if bookmark:
            raise AlreadyExistsException
        new_bookmark = await self.model(
            user_id=user_id,
            film_id=film_id,
            created_at=datetime.now(UTC),
        ).insert()  # noqa
        return new_bookmark.id

    async def get_by_user_id(self, user_id: str) -> list[Bookmark]:
        bookmarks = await self.model.find(
            self.model.user_id == UUID(user_id),
            self.model.is_deleted == False,  # noqa
        ).to_list()
        return bookmarks

    async def delete(self, user_id: str, film_id: UUID):
        bookmark = await self._get_one(user_id, film_id)
        if not bookmark:
            raise NotFoundException
        bookmark.is_deleted = True
        bookmark.updated_at = datetime.now(UTC)
        await bookmark.save()  # noqa
