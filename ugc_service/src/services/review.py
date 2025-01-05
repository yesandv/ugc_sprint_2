from datetime import datetime, UTC
from uuid import UUID

from ugc_service.src.core.exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from ugc_service.src.models.like import Like
from ugc_service.src.models.review import Review
from ugc_service.src.schemas.review import ReviewInput, ReviewOutput


class ReviewService:

    def __init__(self):
        self.model = Review
        self.like_collection = Like.get_collection_name()

    async def _get_one(self, user_id: str, film_id: UUID) -> Review:
        return await self.model.find_one(
            self.model.user_id == UUID(user_id),
            self.model.film_id == film_id,
            self.model.is_deleted == False,  # noqa
        )

    async def create(self, user_id: str, review_input: ReviewInput) -> UUID:
        review = await self._get_one(user_id, review_input.film_id)
        if review:
            raise AlreadyExistsException
        new_review = await self.model(
            user_id=user_id,
            film_id=review_input.film_id,
            text=review_input.text,
            created_at=datetime.now(UTC),
        ).insert()  # noqa
        return new_review.id

    async def get_all(
            self, user_id: str = None, film_id: UUID = None
    ) -> list[ReviewOutput]:
        filters = {"is_deleted": False}
        if user_id:
            filters["user_id"] = UUID(user_id)
        elif film_id:
            filters["film_id"] = film_id
        pipeline = [
            {
                "$lookup": {
                    "from": self.like_collection,
                    "localField": "film_id",
                    "foreignField": "film_id",
                    "as": "likes",
                }
            },
            {
                "$unwind": {
                    "path": "$likes",
                    "preserveNullAndEmptyArrays": True,
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "film_id": 1,
                    "text": 1,
                    "rating": "$likes.rating",
                }
            }
        ]
        return await self.model.find(filters).aggregate(
            pipeline, projection_model=ReviewOutput
        ).to_list()

    async def update(self, user_id: str, review_input: ReviewInput):
        review = await self._get_one(user_id, review_input.film_id)
        if not review:
            raise NotFoundException
        review.text = review_input.text
        review.updated_at = datetime.now(UTC)
        await review.save()  # noqa

    async def delete(self, user_id: str, film_id: UUID):
        review = await self._get_one(user_id, film_id)
        if not review:
            raise NotFoundException
        review.is_deleted = True
        review.updated_at = datetime.now(UTC)
        await review.save()  # noqa
