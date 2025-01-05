from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    project_name: str = "UGC Activity Service"
    mongo_host: str = "localhost"
    mongo_port: int = "27017"
    mongo_db: str = "mongoDb"
    bookmark_collection: str = ""
    like_collection: str = ""
    review_collection: str = ""
    jwt_secret_key: str = "secret"
    jwt_algorithm: str = ""
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env", extra="ignore"
    )

    @property
    def mongo_url(self):
        return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_db}"


app_settings = Settings()
