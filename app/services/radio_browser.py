"""Radio Browser API client for searching internet radio stations."""

import requests
from typing import Optional

API_BASE = "https://de1.api.radio-browser.info/json"
USER_AGENT = "RadioPlayerApp/1.0"


def search_stations(
    query: str, limit: int = 30, timeout: int = 10
) -> list[dict]:
    """Search for radio stations by name.

    Returns a list of dicts with keys: name, url, country, tags, favicon.
    """
    try:
        resp = requests.get(
            f"{API_BASE}/stations/byname/{query}",
            params={"limit": limit, "order": "clickcount", "reverse": "true"},
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        resp.raise_for_status()
        results = resp.json()

        stations = []
        for r in results:
            url = r.get("url_resolved") or r.get("url", "")
            if not url:
                continue
            stations.append(
                {
                    "name": r.get("name", "Unknown"),
                    "url": url,
                    "country": r.get("country", ""),
                    "tags": r.get("tags", ""),
                    "favicon": r.get("favicon", ""),
                    "codec": r.get("codec", ""),
                    "bitrate": r.get("bitrate", 0),
                }
            )
        return stations

    except requests.RequestException:
        return []
