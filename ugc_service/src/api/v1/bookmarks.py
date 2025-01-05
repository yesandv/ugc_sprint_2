from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ugc_service.src.core.exceptions import (
    AlreadyExistsException,
    NotFoundException,
)
from ugc_service.src.core.jwt import security_jwt
from ugc_service.src.schemas.bookmark import BookmarkOutput
from ugc_service.src.schemas.common import NewDocument
from ugc_service.src.services.bookmark import BookmarkService

router = APIRouter(prefix="/api/v1/bookmarks", tags=["BookmarkService"])


@router.post(
    "",
    response_model=NewDocument,
    status_code=HTTPStatus.CREATED,
    description="Add a bookmark",
)
async def add_bookmark(
        film_id: UUID,
        bookmark_service: BookmarkService = Depends(BookmarkService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        doc_id = await bookmark_service.create(user_id, film_id)
        return NewDocument(id=doc_id)
    except AlreadyExistsException:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Bookmark is already added",
        )


@router.get(
    "",
    response_model=list[BookmarkOutput],
    status_code=HTTPStatus.OK,
    description="Get all bookmarks added by the current user",
)
async def get_bookmarks(
        bookmark_service: BookmarkService = Depends(BookmarkService),
        token: dict = Depends(security_jwt),  # noqa
) -> list[BookmarkOutput]:
    user_id = token.get("user_id")
    bookmarks = await bookmark_service.get_by_user_id(user_id)
    return [BookmarkOutput(**bookmark.model_dump()) for bookmark in bookmarks]


@router.delete(
    "",
    status_code=HTTPStatus.OK,
    description="Delete a bookmark",
)
async def delete_bookmark(
        film_id: UUID,
        bookmark_service: BookmarkService = Depends(BookmarkService),
        token: dict = Depends(security_jwt),  # noqa
):
    user_id = token.get("user_id")
    try:
        await bookmark_service.delete(user_id, film_id)
    except NotFoundException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Bookmark was not found",
        )
