from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    detail: str | None = None
