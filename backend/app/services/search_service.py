import asyncio
import logging
from typing import Any

from app.schemas.business import Business
from app.services.providers.osm_provider import OSMProvider
from app.services.scraper_service import ScraperService
from app.services.website_discovery_service import WebsiteDiscoveryService

logger = logging.getLogger(__name__)


class SearchService:
    """Orchestrate OSM search, website discovery, scraping, and merge logic."""

    def __init__(
        self,
        osm_provider: OSMProvider | None = None,
        website_service: WebsiteDiscoveryService | None = None,
        scraper_service: ScraperService | None = None,
    ) -> None:
        self.osm_provider = osm_provider or OSMProvider()
        self.website_service = website_service or WebsiteDiscoveryService()
        self.scraper_service = scraper_service or ScraperService()

    async def search(
        self,
        location: str,
        category: str,
        limit: int,
        popularity_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return OSM businesses enriched with website and scraped contact data."""
        businesses = await self.osm_provider.search_businesses(
            location=location,
            category=category,
            limit=limit,
            popularity_filter=popularity_filter,
        )

        enriched = await asyncio.gather(
            *[
                self._enrich_business(business=business, location=location)
                for business in businesses
            ],
            return_exceptions=True,
        )

        results: list[dict[str, Any]] = []
        for item, original in zip(enriched, businesses, strict=False):
            if isinstance(item, Exception):
                logger.exception("Business enrichment failed for %s", original.name, exc_info=item)
                results.append(original.model_dump())
                continue

            results.append(item.model_dump())

        return self._filter_by_popularity(results, popularity_filter)

    async def _enrich_business(self, business: Business, location: str) -> Business:
        website = business.website

        if not website and business.name:
            website = await self.website_service.find_website(
                business_name=business.name,
                city=business.city or location,
            )

        scraped_data: dict[str, Any] = {}
        if website:
            scraped_data = await self.scraper_service.scrape(website)

        candidate = business.model_copy(update={"website": website or business.website})
        return self._merge_business(candidate, scraped_data)

    def _merge_business(self, business: Business, scraped_data: dict[str, Any]) -> Business:
        """Merge scraper values without overwriting OpenStreetMap values."""
        merged = business.model_dump()

        osm_first_fields = ("address", "city", "state", "country", "phone", "website", "email")
        for field in osm_first_fields:
            if not merged.get(field) and scraped_data.get(field):
                merged[field] = scraped_data[field]

        social_fields = ("instagram", "facebook", "linkedin", "whatsapp")
        for field in social_fields:
            if not merged.get(field) and scraped_data.get(field):
                merged[field] = scraped_data[field]

        enriched = Business(**merged)
        enriched.popularity_score = self._calculate_popularity_score(enriched)
        return enriched

    def _calculate_popularity_score(self, business: Business) -> int:
        score = 0
        for field, weight in {
            "website": 20,
            "phone": 20,
            "email": 15,
            "address": 15,
            "instagram": 8,
            "facebook": 8,
            "linkedin": 6,
            "whatsapp": 8,
        }.items():
            if getattr(business, field):
                score += weight

        if business.rating is not None:
            score += min(int(business.rating * 5), 25)
        if business.review_count is not None:
            score += min(business.review_count, 25)

        return min(score, 100)

    def _filter_by_popularity(
        self,
        businesses: list[dict[str, Any]],
        popularity_filter: str | None,
    ) -> list[dict[str, Any]]:
        if not popularity_filter:
            return businesses

        thresholds = {
            "high": 70,
            "medium": 40,
            "low": 1,
        }
        minimum_score = thresholds.get(popularity_filter.lower())
        if minimum_score is None:
            return businesses

        return [
            business
            for business in businesses
            if (business.get("popularity_score") or 0) >= minimum_score
        ]
