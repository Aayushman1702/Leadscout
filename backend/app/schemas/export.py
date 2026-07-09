from pydantic import BaseModel, Field

from app.schemas.business import Business


class ExportRequest(BaseModel):
    businesses: list[Business] = Field(default_factory=list)
