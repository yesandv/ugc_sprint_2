from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ugc_service.src.core.exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from ugc_service.src.core.jwt import security_jwt
from ugc_service.src.schemas.common import NewDocument
from ugc_service.src.schemas.like import LikeInput, LikeOutput
from ugc_service.src.services.like import LikeService

router = APIRouter(prefix="/api/v1/likes", tags=["LikeService"])


@router.post(
    "",
    response_model=NewDocument,
    status_code=HTTPStatus.CREATED,
    description="Add a like to a film",
)
async def add_like(
        like_input: LikeInput,
        like_service: LikeService = Depends(LikeService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        doc_id = await like_service.create(user_id, like_input)
        return NewDocument(id=doc_id)
    except AlreadyExistsException:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="The like already exists",
        )


@router.get(
    "",
    response_model=list[LikeOutput],
    status_code=HTTPStatus.OK,
    description="Get all likes added by the current user",
)
async def get_likes(
        like_service: LikeService = Depends(LikeService),
        token: dict = Depends(security_jwt),  # noqa
) -> list[LikeOutput]:
    user_id = token.get("user_id")
    likes = await like_service.get_by_user_id(user_id)
    return [LikeOutput(**like.model_dump()) for like in likes]


@router.get(
    "/{film_id}/count",
    response_model=int,
    status_code=HTTPStatus.OK,
    description="Get the total number of likes for a film",
)
async def get_like_count(
        film_id: UUID,
        like_service: LikeService = Depends(LikeService),
        token: dict = Depends(security_jwt),  # noqa
) -> int:
    return await like_service.count_by_film_id(film_id)


@router.get(
    "/{film_id}/average-rating",
    response_model=float,
    status_code=HTTPStatus.OK,
    description="Get the average rating for a film",
)
async def get_average_rating(
        film_id: UUID,
        like_service: LikeService = Depends(LikeService),
        token: dict = Depends(security_jwt),  # noqa
) -> float:
    try:
        return await like_service.calculate_average_rating(film_id)
    except NotFoundException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The film was not found",
        )


@router.patch(
    "",
    status_code=HTTPStatus.OK,
    description="Update the rating of an existing like",
)
async def update_rating(
        like_input: LikeInput,
        like_service: LikeService = Depends(LikeService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        await like_service.update(user_id, like_input)
    except NotFoundException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The like does not exist",
        )


@router.delete(
    "",
    status_code=HTTPStatus.OK,
    description="Remove a like from a specific film",
)
async def delete_like(
        film_id: UUID,
        like_service: LikeService = Depends(LikeService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        await like_service.delete(user_id, film_id)
    except NotFoundException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The like does not exist",
        )
