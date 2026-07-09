import logging
import os
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

EXCLUDED_DOMAINS = (
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "justdial.com",
    "tripadvisor.",
    "zomato.com",
    "swiggy.com",
)


class WebsiteDiscoveryService:
    """Find official websites using Serper."""

    BASE_URL = "https://google.serper.dev/search"

    def __init__(self) -> None:
        self.api_key = os.getenv("SERPER_API_KEY")

    async def find_website(self, business_name: str, city: str = "") -> str:
        """Find the most likely official website for a business."""
        if not self.api_key:
            logger.info("SERPER_API_KEY is not configured; skipping website discovery")
            return ""

        query = f"{business_name} {city} official website".strip()
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": 5}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(self.BASE_URL, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Serper website discovery failed for %s: %s", business_name, exc)
            return ""

        organic = response.json().get("organic", [])
        for result in organic:
            link = result.get("link", "")
            if link and self._looks_official(link):
                return link

        return organic[0].get("link", "") if organic else ""

    def _looks_official(self, url: str) -> bool:
        domain = urlparse(url).netloc.lower()
        return not any(excluded in domain for excluded in EXCLUDED_DOMAINS)
