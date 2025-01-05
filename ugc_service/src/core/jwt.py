from http import HTTPStatus

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from jwt import DecodeError, ExpiredSignatureError

from ugc_service.src.core.settings import app_settings


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials = await super().__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid or missing Bearer token",
            )
        try:
            decoded_token = self.parse_token(credentials.credentials)
        except (DecodeError, ExpiredSignatureError):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token",
            )
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict:
        payload = jwt.decode(
            jwt_token,
            app_settings.jwt_secret_key,
            algorithms=[app_settings.jwt_algorithm],
        )
        return payload


security_jwt = JWTBearer()
