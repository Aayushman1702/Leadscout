from fastapi import APIRouter

from app.services.scraper_service import ScraperService

router = APIRouter()

scraper = ScraperService()


@router.get("/test-scraper")
async def test_scraper():

    data = await scraper.scrape(
        "https://marzorin.com"
    )

    return data