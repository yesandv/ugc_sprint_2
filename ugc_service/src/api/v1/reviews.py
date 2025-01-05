from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ugc_service.src.core.exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from ugc_service.src.core.jwt import security_jwt
from ugc_service.src.schemas.common import NewDocument
from ugc_service.src.schemas.review import ReviewInput, ReviewOutput
from ugc_service.src.services.review import ReviewService

router = APIRouter(prefix="/api/v1/reviews", tags=["ReviewService"])


@router.post(
    "",
    response_model=NewDocument,
    status_code=HTTPStatus.CREATED,
    description="Add a review",
)
async def add_review(
        review_input: ReviewInput,
        review_service: ReviewService = Depends(ReviewService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        doc_id = await review_service.create(user_id, review_input)
        return NewDocument(id=doc_id)
    except AlreadyExistsException:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Review is already added",
        )


@router.get(
    "",
    response_model=list[ReviewOutput],
    status_code=HTTPStatus.OK,
    description="Get all reviews added by the current user",
)
async def get_reviews_by_user_id(
        review_service: ReviewService = Depends(ReviewService),
        token: dict = Depends(security_jwt),  # noqa
) -> list[ReviewOutput]:
    user_id = token.get("user_id")
    return await review_service.get_all(user_id=user_id)


@router.get(
    "/{film_id}/all",
    response_model=list[ReviewOutput],
    status_code=HTTPStatus.OK,
    description="Get all film reviews",
)
async def get_film_reviews(
        film_id: UUID,
        review_service: ReviewService = Depends(ReviewService),
        token: dict = Depends(security_jwt),  # noqa
) -> list[ReviewOutput]:
    return await review_service.get_all(film_id=film_id)


@router.patch("", status_code=HTTPStatus.OK, description="Update the review")
async def update_review(
        review_input: ReviewInput,
        review_service: ReviewService = Depends(ReviewService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        await review_service.update(user_id, review_input)
    except NotFoundException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The review does not exist",
        )


@router.delete("", status_code=HTTPStatus.OK, description="Delete the review")
async def delete_review(
        film_id: UUID,
        review_service: ReviewService = Depends(ReviewService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        await review_service.delete(user_id, film_id)
    except NotFoundException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The review does not exist",
        )
