from pydantic import BaseModel


class Business(BaseModel):
    name: str = ""
    category: str = ""

    address: str = ""
    city: str = ""
    state: str = ""
    country: str = ""

    phone: str = ""
    website: str = ""
    email: str = ""

    instagram: str = ""
    facebook: str = ""
    linkedin: str = ""
    whatsapp: str = ""

    source: str = "OpenStreetMap"
    lead_score: int | None = None
    rating: float | None = None
    review_count: int | None = None
    popularity_score: int | None = None
