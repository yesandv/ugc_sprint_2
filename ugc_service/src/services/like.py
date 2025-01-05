from datetime import datetime, UTC
from uuid import UUID

from ugc_service.src.core.exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from ugc_service.src.models.like import Like
from ugc_service.src.schemas.like import LikeInput


class LikeService:

    def __init__(self):
        self.model = Like

    async def _get_one(self, user_id: str, film_id: UUID) -> Like:
        return await self.model.find_one(
            self.model.user_id == UUID(user_id),
            self.model.film_id == film_id,
            self.model.is_deleted == False,  # noqa
        )

    async def create(self, user_id: str, like_input: LikeInput) -> UUID:
        like = await self._get_one(user_id, like_input.film_id)
        if like:
            raise AlreadyExistsException
        new_like = await self.model(
            user_id=user_id,
            film_id=like_input.film_id,
            rating=like_input.rating,
            created_at=datetime.now(UTC),
        ).insert()  # noqa
        return new_like.id

    async def get_by_user_id(self, user_id: str) -> list[Like]:
        likes = await self.model.find(
            self.model.user_id == UUID(user_id),
            self.model.is_deleted == False,  # noqa
        ).to_list()
        return likes

    async def count_by_film_id(self, film_id: UUID) -> int:
        count = await self.model.find(
            self.model.film_id == film_id,
            self.model.is_deleted == False,  # noqa
        ).count()
        return count

    async def calculate_average_rating(self, film_id) -> float:
        avg = await self.model.find(
            self.model.film_id == film_id,
            self.model.is_deleted == False,  # noqa
        ).avg(self.model.rating)
        if not avg:
            raise NotFoundException
        return avg

    async def update(self, user_id: str, like_input: LikeInput):
        like = await self._get_one(user_id, like_input.film_id)
        if not like:
            raise NotFoundException
        like.rating = like_input.rating
        like.updated_at = datetime.now(UTC)
        await like.save()  # noqa

    async def delete(self, user_id: str, film_id: UUID):
        like = await self._get_one(user_id, film_id)
        if not like:
            raise NotFoundException
        like.is_deleted = True
        like.updated_at = datetime.now(UTC)
        await like.save()  # noqa
