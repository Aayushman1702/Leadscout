import math
from typing import Any

import httpx

from app.schemas.business import Business

USER_AGENT = "LeadScoutAI/1.0"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
DEFAULT_COUNTRY_CODE = "in"
OVERPASS_URLS = (
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
)
SEARCH_RADIUS_METERS = 12000
FALLBACK_RADIUS_METERS = 25000
CACHED_CITY_BOUNDING_BOX_DELTA = 0.18
CACHED_LOCALITY_BOUNDING_BOX_DELTA = 0.04
LOCALITY_SEARCH_RADIUS_METERS = 6000
LOCALITY_FALLBACK_RADIUS_METERS = 10000

MUMBAI_LOCATION_CACHE: dict[str, tuple[float, float]] = {
    "aarey": (19.1547, 72.8813),
    "andheri": (19.1136, 72.8697),
    "andheri east": (19.1155, 72.8727),
    "andheri west": (19.1364, 72.8296),
    "antop hill": (19.0208, 72.8667),
    "bandra": (19.0596, 72.8295),
    "bandra east": (19.0550, 72.8407),
    "bandra west": (19.0596, 72.8295),
    "bhandup": (19.1511, 72.9372),
    "bhandup east": (19.1445, 72.9480),
    "bhandup west": (19.1511, 72.9372),
    "bhayandar": (19.3015, 72.8510),
    "bhayander": (19.3015, 72.8510),
    "boisar": (19.8037, 72.7550),
    "borivali": (19.2307, 72.8567),
    "borivali east": (19.2241, 72.8665),
    "borivali west": (19.2361, 72.8448),
    "byculla": (18.9766, 72.8328),
    "chembur": (19.0622, 72.9005),
    "churchgate": (18.9322, 72.8264),
    "colaba": (18.9067, 72.8147),
    "cotton green": (18.9860, 72.8449),
    "cuffe parade": (18.9127, 72.8213),
    "dadar": (19.0178, 72.8478),
    "dadar east": (19.0189, 72.8479),
    "dadar west": (19.0180, 72.8393),
    "dahisar": (19.2575, 72.8596),
    "dahisar east": (19.2518, 72.8653),
    "dahisar west": (19.2502, 72.8440),
    "deonar": (19.0488, 72.9136),
    "dockyard road": (18.9664, 72.8441),
    "fort": (18.9333, 72.8333),
    "ghatkopar": (19.0856, 72.9082),
    "ghatkopar east": (19.0850, 72.9183),
    "ghatkopar west": (19.0895, 72.9007),
    "girgaon": (18.9543, 72.8179),
    "goregaon": (19.1663, 72.8526),
    "goregaon east": (19.1697, 72.8553),
    "goregaon west": (19.1648, 72.8493),
    "goregaon mumbai": (19.1663, 72.8526),
    "govandi": (19.0556, 72.9156),
    "grant road": (18.9633, 72.8136),
    "jogeshwari": (19.1364, 72.8488),
    "jogeshwari east": (19.1376, 72.8613),
    "jogeshwari west": (19.1405, 72.8422),
    "juhu": (19.1075, 72.8263),
    "kalbadevi": (18.9492, 72.8272),
    "kanjurmarg": (19.1294, 72.9328),
    "kandivali": (19.2058, 72.8643),
    "kandivali east": (19.2031, 72.8727),
    "kandivali west": (19.2071, 72.8426),
    "khar": (19.0690, 72.8390),
    "khar west": (19.0690, 72.8390),
    "kharghar": (19.0473, 73.0699),
    "kurla": (19.0726, 72.8845),
    "lalbaug": (18.9907, 72.8360),
    "lower parel": (18.9955, 72.8308),
    "mahalaxmi": (18.9822, 72.8247),
    "mahim": (19.0350, 72.8408),
    "malabar hill": (18.9548, 72.7985),
    "malad": (19.1874, 72.8484),
    "malad east": (19.1867, 72.8560),
    "malad west": (19.1840, 72.8400),
    "mandvi": (18.9540, 72.8357),
    "mankhurd": (19.0480, 72.9322),
    "marol": (19.1192, 72.8828),
    "marine lines": (18.9440, 72.8230),
    "matunga": (19.0269, 72.8553),
    "matunga east": (19.0269, 72.8553),
    "matunga west": (19.0300, 72.8404),
    "mazgaon": (18.9687, 72.8435),
    "mira road": (19.2813, 72.8686),
    "mulund": (19.1726, 72.9425),
    "mulund east": (19.1686, 72.9562),
    "mulund west": (19.1726, 72.9425),
    "nahur": (19.1547, 72.9460),
    "navi mumbai": (19.0330, 73.0297),
    "nerul": (19.0330, 73.0189),
    "parel": (19.0095, 72.8377),
    "powai": (19.1176, 72.9060),
    "prabhadevi": (19.0166, 72.8295),
    "sakinaka": (19.1027, 72.8870),
    "santacruz": (19.0822, 72.8417),
    "santacruz east": (19.0800, 72.8500),
    "santacruz west": (19.0822, 72.8417),
    "seawoods": (19.0219, 73.0182),
    "sion": (19.0434, 72.8633),
    "tardeo": (18.9676, 72.8141),
    "thane": (19.2183, 72.9781),
    "trombay": (19.0190, 72.9230),
    "vashi": (19.0770, 72.9986),
    "versova": (19.1351, 72.8146),
    "vidyavihar": (19.0790, 72.8976),
    "vikhroli": (19.1111, 72.9289),
    "vile parle": (19.0968, 72.8517),
    "vile parle east": (19.0968, 72.8517),
    "vile parle west": (19.1030, 72.8400),
    "wadala": (19.0176, 72.8562),
    "worli": (19.0176, 72.8167),
}

INDIA_LOCATION_CACHE: dict[str, tuple[float, float]] = {
    "agartala": (23.8315, 91.2868),
    "agartala tripura": (23.8315, 91.2868),
    "ahmedabad": (23.0225, 72.5714),
    "ajmer": (26.4499, 74.6399),
    "allahabad": (25.4358, 81.8463),
    "prayagraj": (25.4358, 81.8463),
    "amritsar": (31.6340, 74.8723),
    "aurangabad": (19.8762, 75.3433),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "bhopal": (23.2599, 77.4126),
    "bhubaneswar": (20.2961, 85.8245),
    "chandigarh": (30.7333, 76.7794),
    "chennai": (13.0827, 80.2707),
    "coimbatore": (11.0168, 76.9558),
    "dehradun": (30.3165, 78.0322),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "dhanbad": (23.7957, 86.4304),
    "faridabad": (28.4089, 77.3178),
    "ghaziabad": (28.6692, 77.4538),
    "goa": (15.2993, 74.1240),
    "gurgaon": (28.4595, 77.0266),
    "gurugram": (28.4595, 77.0266),
    "guwahati": (26.1445, 91.7362),
    "gwalior": (26.2183, 78.1828),
    "hyderabad": (17.3850, 78.4867),
    "indore": (22.7196, 75.8577),
    "jaipur": (26.9124, 75.7873),
    "jalandhar": (31.3260, 75.5762),
    "jammu": (32.7266, 74.8570),
    "jamshedpur": (22.8046, 86.2029),
    "jodhpur": (26.2389, 73.0243),
    "kanpur": (26.4499, 80.3319),
    "kochi": (9.9312, 76.2673),
    "cochin": (9.9312, 76.2673),
    "kolkata": (22.5726, 88.3639),
    "lucknow": (26.8467, 80.9462),
    "ludhiana": (30.9010, 75.8573),
    "madurai": (9.9252, 78.1198),
    "mangalore": (12.9141, 74.8560),
    "meerut": (28.9845, 77.7064),
    "mumbai": (19.0760, 72.8777),
    **MUMBAI_LOCATION_CACHE,
    "mysore": (12.2958, 76.6394),
    "mysuru": (12.2958, 76.6394),
    "nagpur": (21.1458, 79.0882),
    "nala sopara": (19.4154, 72.8613),
    "nalasopara": (19.4154, 72.8613),
    "nashik": (19.9975, 73.7898),
    "noida": (28.5355, 77.3910),
    "panipat": (29.3909, 76.9635),
    "patna": (25.5941, 85.1376),
    "pune": (18.5204, 73.8567),
    "raipur": (21.2514, 81.6296),
    "rajkot": (22.3039, 70.8022),
    "ranchi": (23.3441, 85.3096),
    "shimla": (31.1048, 77.1734),
    "silchar": (24.8333, 92.7789),
    "solan": (30.9045, 77.0967),
    "solan himachal pradesh": (30.9045, 77.0967),
    "srinagar": (34.0837, 74.7973),
    "surat": (21.1702, 72.8311),
    "thane": (19.2183, 72.9781),
    "thiruvananthapuram": (8.5241, 76.9366),
    "trivandrum": (8.5241, 76.9366),
    "udaipur": (24.5854, 73.7125),
    "vadodara": (22.3072, 73.1812),
    "baroda": (22.3072, 73.1812),
    "varanasi": (25.3176, 82.9739),
    "vijayawada": (16.5062, 80.6480),
    "visakhapatnam": (17.6868, 83.2185),
    "vizag": (17.6868, 83.2185),
}

LOCALITY_CACHE_KEYS = set(MUMBAI_LOCATION_CACHE) | {"nala sopara", "nalasopara"}

CATEGORY_OPTIONS: dict[str, dict[str, Any]] = {
    "all": {
        "label": "All Businesses",
        "queries": [
            ("amenity", "*"),
            ("shop", "*"),
            ("tourism", "*"),
            ("office", "*"),
            ("healthcare", "*"),
            ("leisure", "*"),
        ],
    },
    "cafe": {
        "label": "Cafe",
        "queries": [("amenity", "cafe"), ("shop", "coffee")],
    },
    "restaurant": {
        "label": "Restaurant",
        "queries": [
            ("amenity", "restaurant"),
            ("amenity", "fast_food"),
            ("amenity", "food_court"),
            ("amenity", "cafe"),
            ("shop", "food"),
        ],
    },
    "food": {
        "label": "Food & Snacks",
        "queries": [
            ("amenity", "restaurant"),
            ("amenity", "cafe"),
            ("amenity", "fast_food"),
            ("amenity", "food_court"),
            ("shop", "bakery"),
            ("shop", "confectionery"),
        ],
    },
    "hotel": {
        "label": "Hotel",
        "queries": [
            ("tourism", "hotel"),
            ("tourism", "guest_house"),
            ("tourism", "hostel"),
            ("tourism", "motel"),
        ],
    },
    "clinic": {
        "label": "Clinic",
        "queries": [("amenity", "clinic"), ("healthcare", "clinic"), ("amenity", "doctors")],
    },
    "hospital": {
        "label": "Hospital",
        "queries": [("amenity", "hospital"), ("healthcare", "hospital")],
    },
    "pharmacy": {
        "label": "Pharmacy",
        "queries": [("amenity", "pharmacy"), ("healthcare", "pharmacy"), ("shop", "chemist")],
    },
    "bakery": {
        "label": "Bakery",
        "queries": [("shop", "bakery"), ("shop", "confectionery")],
    },
    "supermarket": {
        "label": "Supermarket",
        "queries": [("shop", "supermarket"), ("shop", "convenience")],
    },
    "gym": {
        "label": "Gym / Fitness",
        "queries": [
            ("leisure", "fitness_centre"),
            ("leisure", "sports_centre"),
            ("sport", "fitness"),
        ],
    },
    "beauty_salon": {
        "label": "Beauty Salon",
        "queries": [("shop", "beauty"), ("shop", "hairdresser")],
    },
    "jewelry": {
        "label": "Jewelry",
        "queries": [("shop", "jewelry"), ("shop", "jewellery")],
    },
    "clothes": {
        "label": "Clothing Store",
        "queries": [("shop", "clothes"), ("shop", "fashion"), ("shop", "boutique")],
    },
    "dentist": {
        "label": "Dentist",
        "queries": [("amenity", "dentist"), ("healthcare", "dentist")],
    },
    "school": {
        "label": "School",
        "queries": [("amenity", "school"), ("amenity", "college")],
    },
    "bank": {
        "label": "Bank",
        "queries": [("amenity", "bank"), ("amenity", "atm")],
    },
    "electronics": {
        "label": "Electronics",
        "queries": [("shop", "electronics"), ("shop", "mobile_phone"), ("shop", "computer")],
    },
}


class OSMProvider:
    """Fetch business candidates from OpenStreetMap."""

    _geocode_cache: dict[str, dict[str, Any] | None] = {}

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": USER_AGENT}

    def get_categories(self) -> list[dict[str, str]]:
        """Return supported categories for UI dropdowns."""
        return [
            {"value": value, "label": config["label"]}
            for value, config in CATEGORY_OPTIONS.items()
        ]

    async def geocode(self, location: str) -> dict[str, Any] | None:
        """Return coordinates and bounding box for a location name."""
        cache_key = location.strip().lower()
        if cache_key in self._geocode_cache:
            return self._geocode_cache[cache_key]

        cached_location = self._cached_location_result(location)
        if cached_location:
            self._geocode_cache[cache_key] = cached_location
            return cached_location

        attempt_groups = self._build_geocode_attempt_groups(location)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempts in attempt_groups:
                for attempt in attempts:
                    params = {
                        **attempt,
                        "format": "json",
                        "limit": 5,
                        "addressdetails": 1,
                    }
                    try:
                        response = await client.get(
                            NOMINATIM_URL,
                            params=params,
                            headers=self.headers,
                        )
                        response.raise_for_status()
                    except httpx.HTTPStatusError as exc:
                        if exc.response.status_code == 429:
                            cached_location = self._cached_location_result(location)
                            if cached_location:
                                self._geocode_cache[cache_key] = cached_location
                                return cached_location
                        raise

                    candidates = response.json()

                    if candidates:
                        result = self._format_geocode_result(
                            max(candidates, key=self._score_geocode_result)
                        )
                        self._geocode_cache[cache_key] = result
                        return result

        self._geocode_cache[cache_key] = None
        return None

    def _cached_location_result(self, location: str) -> dict[str, Any] | None:
        for term in self._location_terms(location):
            normalized_term = term.lower()
            coordinates = INDIA_LOCATION_CACHE.get(normalized_term)
            if coordinates:
                latitude, longitude = coordinates
                is_locality = normalized_term in LOCALITY_CACHE_KEYS
                delta = (
                    CACHED_LOCALITY_BOUNDING_BOX_DELTA
                    if is_locality
                    else CACHED_CITY_BOUNDING_BOX_DELTA
                )
                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "boundingbox": [
                        latitude - delta,
                        latitude + delta,
                        longitude - delta,
                        longitude + delta,
                    ],
                    "search_radius": (
                        LOCALITY_SEARCH_RADIUS_METERS
                        if is_locality
                        else SEARCH_RADIUS_METERS
                    ),
                    "fallback_radius": (
                        LOCALITY_FALLBACK_RADIUS_METERS
                        if is_locality
                        else FALLBACK_RADIUS_METERS
                    ),
                }

        return None

    def _format_geocode_result(self, best_result: dict[str, Any]) -> dict[str, Any]:
        return {
            "latitude": float(best_result["lat"]),
            "longitude": float(best_result["lon"]),
            "boundingbox": [
                float(value)
                for value in best_result.get("boundingbox", [])
            ],
        }

    def _build_geocode_attempt_groups(self, location: str) -> list[list[dict[str, str]]]:
        """Build forgiving India-first geocode attempts for city/locality names."""
        terms = self._location_terms(location)
        return [
            self._unique_attempts(
                {"q": term, "countrycodes": DEFAULT_COUNTRY_CODE}
                for term in terms
            ),
            self._unique_attempts({"q": f"{term}, India"} for term in terms),
            self._unique_attempts({"q": term} for term in terms),
        ]

    def _unique_attempts(self, attempts: Any) -> list[dict[str, str]]:
        unique_attempts: list[dict[str, str]] = []
        seen: set[tuple[tuple[str, str], ...]] = set()
        for attempt in attempts:
            key = tuple(sorted(attempt.items()))
            if key not in seen:
                seen.add(key)
                unique_attempts.append(attempt)
        return unique_attempts

    def _location_terms(self, location: str) -> list[str]:
        primary_location = location.split(",", maxsplit=1)[0]
        cleaned = " ".join(
            location.replace(",", " ")
            .replace("-", " ")
            .replace("_", " ")
            .split()
        )
        primary_cleaned = " ".join(
            primary_location.replace("-", " ").replace("_", " ").split()
        )
        compact = cleaned.replace(" ", "")
        lower_compact = compact.lower()
        terms = []

        if primary_cleaned and primary_cleaned != cleaned:
            terms.append(primary_cleaned)

        if "sopara" in lower_compact and "nala sopara" not in cleaned.lower():
            terms.append("Nala Sopara")

        terms.append(cleaned)

        if compact and compact != cleaned:
            terms.append(compact)

        if cleaned.lower().endswith("pur") and " " not in cleaned:
            terms.append(cleaned[:-3] + " pur")

        return [term for term in dict.fromkeys(terms) if term]

    def _score_geocode_result(self, result: dict[str, Any]) -> float:
        address = result.get("address", {})
        result_class = result.get("class", "")
        result_type = result.get("type", "")
        importance = float(result.get("importance") or 0)
        score = importance * 10

        if address.get("country_code") == DEFAULT_COUNTRY_CODE:
            score += 50

        if result_class in {"boundary", "place"}:
            score += 30
        elif result_class in {"amenity", "shop", "tourism", "office"}:
            score -= 25

        if result_type in {
            "city",
            "town",
            "suburb",
            "village",
            "municipality",
            "administrative",
        }:
            score += 25

        bbox = [float(value) for value in result.get("boundingbox", [])]
        if len(bbox) == 4:
            area = abs((bbox[1] - bbox[0]) * (bbox[3] - bbox[2]))
            if 0.0001 <= area <= 5:
                score += 20
            elif area < 0.0001:
                score -= 15

        return score

    async def search_businesses(
        self,
        location: str,
        category: str,
        limit: int,
        popularity_filter: str | None = None,
    ) -> list[Business]:
        """Search OSM for businesses in a category near a location."""
        coordinates = await self.geocode(location)
        if coordinates is None:
            return []

        return await self.search_nearby(
            latitude=coordinates["latitude"],
            longitude=coordinates["longitude"],
            category=category,
            limit=limit,
            boundingbox=coordinates.get("boundingbox"),
            search_radius=coordinates.get("search_radius", SEARCH_RADIUS_METERS),
            fallback_radius=coordinates.get("fallback_radius", FALLBACK_RADIUS_METERS),
            sort_by_popularity=bool(popularity_filter),
        )

    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        category: str,
        limit: int,
        boundingbox: list[float] | None = None,
        search_radius: int = SEARCH_RADIUS_METERS,
        fallback_radius: int = FALLBACK_RADIUS_METERS,
        sort_by_popularity: bool = False,
    ) -> list[Business]:
        """Run broad Overpass queries and convert elements into Business models."""
        normalized_category = category.lower().strip()
        if normalized_category not in CATEGORY_OPTIONS:
            raise ValueError(f"Unsupported category: {category}")

        query = self._build_overpass_query(
            queries=CATEGORY_OPTIONS[normalized_category]["queries"],
            latitude=latitude,
            longitude=longitude,
            limit=limit,
            boundingbox=boundingbox,
            search_radius=search_radius,
            fallback_radius=fallback_radius,
        )

        data = await self._request_overpass(query)

        seen: set[str] = set()
        seen_businesses: set[str] = set()
        businesses_with_distance: list[tuple[float, Business]] = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            if not tags.get("name"):
                continue

            element_id = f"{element.get('type')}:{element.get('id')}"
            if element_id in seen:
                continue

            business = self._element_to_business(element, normalized_category)
            business_key = f"{business.name.lower()}|{business.address.lower()}"
            if business_key in seen_businesses:
                continue

            seen.add(element_id)
            seen_businesses.add(business_key)
            businesses_with_distance.append(
                (
                    self._element_distance_km(element, latitude, longitude),
                    business,
                )
            )

        if sort_by_popularity:
            businesses = [business for _, business in businesses_with_distance]
            businesses.sort(key=lambda business: business.popularity_score or 0, reverse=True)
        else:
            businesses = [
                business
                for _, business in sorted(
                    businesses_with_distance,
                    key=lambda item: item[0],
                )
            ]
        return businesses[:limit]

    def _element_distance_km(
        self,
        element: dict[str, Any],
        latitude: float,
        longitude: float,
    ) -> float:
        element_latitude = element.get("lat") or element.get("center", {}).get("lat")
        element_longitude = element.get("lon") or element.get("center", {}).get("lon")
        if element_latitude is None or element_longitude is None:
            return float("inf")

        return self._distance_km(
            latitude,
            longitude,
            float(element_latitude),
            float(element_longitude),
        )

    def _distance_km(
        self,
        start_latitude: float,
        start_longitude: float,
        end_latitude: float,
        end_longitude: float,
    ) -> float:
        radius_km = 6371.0
        delta_latitude = math.radians(end_latitude - start_latitude)
        delta_longitude = math.radians(end_longitude - start_longitude)
        start_latitude_rad = math.radians(start_latitude)
        end_latitude_rad = math.radians(end_latitude)

        a = (
            math.sin(delta_latitude / 2) ** 2
            + math.cos(start_latitude_rad)
            * math.cos(end_latitude_rad)
            * math.sin(delta_longitude / 2) ** 2
        )
        return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    async def _request_overpass(self, query: str) -> dict[str, Any]:
        """Try multiple Overpass mirrors because public endpoints can timeout."""
        last_error: httpx.HTTPError | None = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for url in OVERPASS_URLS:
                try:
                    response = await client.post(url, data=query, headers=self.headers)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as exc:
                    last_error = exc

        if last_error:
            raise last_error
        return {"elements": []}

    def _build_overpass_query(
        self,
        queries: list[tuple[str, str]],
        latitude: float,
        longitude: float,
        limit: int,
        boundingbox: list[float] | None,
        search_radius: int,
        fallback_radius: int,
    ) -> str:
        selectors = []
        targets = [f"(around:{search_radius},{latitude},{longitude})"]
        if boundingbox and len(boundingbox) == 4:
            south, north, west, east = boundingbox
            targets.insert(0, f"({south},{west},{north},{east})")

        targets.append(f"(around:{fallback_radius},{latitude},{longitude})")

        for key, value in queries:
            for target in dict.fromkeys(targets):
                value_selector = f'["{key}"]' if value == "*" else f'["{key}"="{value}"]'
                selectors.extend(
                    [
                        f"  node{value_selector}{target};",
                        f"  way{value_selector}{target};",
                        f"  relation{value_selector}{target};",
                    ]
                )

        overpass_limit = max(limit * 3, 500)
        return f"""
[out:json][timeout:35];
(
{chr(10).join(selectors)}
);
out center tags qt {overpass_limit};
"""

    def _element_to_business(self, element: dict[str, Any], category: str) -> Business:
        tags = element.get("tags", {})
        rating = self._optional_float(tags, "rating", "stars")
        review_count = self._optional_int(tags, "reviews", "review_count")

        business = Business(
            name=tags.get("name", ""),
            category=category,
            address=self._format_address(tags),
            city=tags.get("addr:city", ""),
            state=tags.get("addr:state", ""),
            country=tags.get("addr:country", ""),
            phone=self._first_tag(tags, "phone", "contact:phone"),
            website=self._first_tag(tags, "website", "contact:website", "url"),
            email=self._first_tag(tags, "email", "contact:email"),
            instagram=self._first_tag(tags, "contact:instagram", "instagram"),
            facebook=self._first_tag(tags, "contact:facebook", "facebook"),
            linkedin=self._first_tag(tags, "contact:linkedin", "linkedin"),
            whatsapp=self._first_tag(tags, "contact:whatsapp", "whatsapp"),
            source="OpenStreetMap",
            rating=rating,
            review_count=review_count,
        )
        business.popularity_score = self._calculate_popularity_score(business)
        return business

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

    def _format_address(self, tags: dict[str, Any]) -> str:
        full_address = tags.get("addr:full")
        if full_address:
            return str(full_address)

        parts = [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:suburb", ""),
            tags.get("addr:city", ""),
            tags.get("addr:postcode", ""),
        ]
        return ", ".join(str(part) for part in parts if part)

    def _first_tag(self, tags: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = tags.get(key)
            if value:
                return str(value)
        return ""

    def _optional_float(self, tags: dict[str, Any], *keys: str) -> float | None:
        value = self._first_tag(tags, *keys)
        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def _optional_int(self, tags: dict[str, Any], *keys: str) -> int | None:
        value = self._first_tag(tags, *keys)
        if not value:
            return None

        try:
            return int(value)
        except ValueError:
            return None
