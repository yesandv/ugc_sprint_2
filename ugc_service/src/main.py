from contextlib import asynccontextmanager

import sentry_sdk
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from ugc_service.src.api.v1 import bookmarks, likes, reviews
from ugc_service.src.core.settings import app_settings
from ugc_service.src.models.bookmark import Bookmark
from ugc_service.src.models.like import Like
from ugc_service.src.models.review import Review


@asynccontextmanager
async def lifespan(_: FastAPI):
    mongo = AsyncIOMotorClient(app_settings.mongo_url)
    db = mongo[app_settings.mongo_db]
    await init_beanie(database=db, document_models=[Bookmark, Like, Review])
    yield
    mongo.close()


sentry_sdk.init(
    dsn=app_settings.sentry_dsn,
    traces_sample_rate=1.0,
)

app = FastAPI(
    title=app_settings.project_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    default_response_class=JSONResponse,
    lifespan=lifespan,
)

app.include_router(bookmarks.router)
app.include_router(likes.router)
app.include_router(reviews.router)
