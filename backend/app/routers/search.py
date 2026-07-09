import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.search import SearchRequest
from app.services.providers.osm_provider import OSMProvider
from app.services.search_service import SearchService

router = APIRouter()
logger = logging.getLogger(__name__)

search_service = SearchService()
osm_provider = OSMProvider()


@router.get("/categories")
async def categories():
    return {"categories": osm_provider.get_categories()}


@router.post("/search")
async def search(data: SearchRequest):
    location_query = data.location
    if data.state:
        location_query = f"{data.location}, {data.state}"

    try:
        businesses = await search_service.search(
            location=location_query,
            category=data.category,
            limit=data.limit,
            popularity_filter=data.popularity_filter,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        logger.warning("Search provider failed: %s", exc)
        return {
            "success": False,
            "location": data.location,
            "state": data.state,
            "category": data.category,
            "total_results": 0,
            "businesses": [],
            "message": "Search provider failed. Please try again later.",
        }

    return {
        "success": True,
        "location": data.location,
        "state": data.state,
        "category": data.category,
        "total_results": len(businesses),
        "businesses": businesses,
    }
