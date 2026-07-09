from fastapi import APIRouter
from app.services.website_discovery_service import WebsiteDiscoveryService

router = APIRouter()

website_service = WebsiteDiscoveryService()


@router.get("/test-website")
async def test_website():

    website = await website_service.find_website(
        business_name="Starbucks",
        city="Pune"
    )

    return {
        "website": website
    }