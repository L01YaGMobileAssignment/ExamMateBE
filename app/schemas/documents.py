from pydantic import BaseModel


class DocumentCreate(BaseModel):
    id: str
    filename: str
    owner: str
    summary: str | None = None
