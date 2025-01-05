from uuid import UUID

from pydantic import BaseModel


class NewDocument(BaseModel):
    id: UUID
