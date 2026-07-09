from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    location: str = Field(..., min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    category: str = Field(..., min_length=2, max_length=100)
    limit: int = Field(default=100, ge=1, le=500)
    popularity_filter: str | None = Field(default=None)
