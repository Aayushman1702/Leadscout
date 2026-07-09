import asyncio
import logging
import re
from collections.abc import Iterable
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CONTACT_PATHS = ("/contact", "/contact-us", "/about", "/reach-us")
LINK_KEYWORDS = ("contact", "contact-us", "contactus", "about", "about-us", "reach", "reach-us")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")


class ScraperService:
    """Scrape contact and social details from a business website."""

    async def scrape(self, website: str) -> dict[str, str]:
        if not website:
            return self._empty_result()

        try:
            normalized_website = self._normalize_url(website)
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                home_html = await self._fetch(client, normalized_website)
                if not home_html:
                    return self._empty_result()

                pages = self._discover_pages(normalized_website, home_html)
                html_pages = await asyncio.gather(
                    *[self._fetch(client, page) for page in pages],
                    return_exceptions=True,
                )

            return self._extract_details(page for page in html_pages if isinstance(page, str))
        except Exception as exc:
            logger.warning("Failed to scrape %s: %s", website, exc)
            return self._empty_result()

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> str:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as exc:
            logger.debug("Skipping page %s: %s", url, exc)
            return ""

    def _discover_pages(self, website: str, html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        pages = {website}

        for path in CONTACT_PATHS:
            pages.add(urljoin(website, path))

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if any(keyword in href.lower() for keyword in LINK_KEYWORDS):
                pages.add(urljoin(website, href))

        return list(pages)

    def _extract_details(self, html_pages: Iterable[str]) -> dict[str, str]:
        emails: set[str] = set()
        phones: set[str] = set()
        result = self._empty_result()

        for html in html_pages:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)

            emails.update(EMAIL_PATTERN.findall(text))
            phones.update(self._clean_phone(phone) for phone in PHONE_PATTERN.findall(text))

            for link in soup.find_all("a", href=True):
                href = link["href"].strip()
                lower_href = href.lower()
                if not result["instagram"] and "instagram.com" in lower_href:
                    result["instagram"] = href
                elif not result["facebook"] and "facebook.com" in lower_href:
                    result["facebook"] = href
                elif not result["linkedin"] and "linkedin.com" in lower_href:
                    result["linkedin"] = href
                elif not result["whatsapp"] and ("wa.me" in lower_href or "whatsapp" in lower_href):
                    result["whatsapp"] = href

        result["email"] = next(iter(emails), "")
        result["phone"] = next((phone for phone in phones if len(re.sub(r"\D", "", phone)) >= 8), "")
        return result

    def _normalize_url(self, website: str) -> str:
        if website.startswith(("http://", "https://")):
            return website
        return f"https://{website}"

    def _clean_phone(self, phone: str) -> str:
        return re.sub(r"\s+", " ", phone).strip(" .-()")

    def _empty_result(self) -> dict[str, str]:
        return {
            "email": "",
            "phone": "",
            "address": "",
            "instagram": "",
            "facebook": "",
            "linkedin": "",
            "whatsapp": "",
        }
