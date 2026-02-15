"""iTunes Search API client for finding podcasts."""

import requests
from typing import Optional


SEARCH_URL = "https://itunes.apple.com/search"


def search_podcasts(query: str, limit: int = 25, timeout: int = 10) -> list[dict]:
    """Search for podcasts via iTunes API.

    Returns a list of dicts with keys: name, artist, feed_url, artwork_url.
    """
    try:
        resp = requests.get(
            SEARCH_URL,
            params={
                "term": query,
                "media": "podcast",
                "limit": limit,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        podcasts = []
        for r in data.get("results", []):
            feed_url = r.get("feedUrl", "")
            if not feed_url:
                continue
            podcasts.append(
                {
                    "name": r.get("collectionName", "Unknown"),
                    "artist": r.get("artistName", ""),
                    "feed_url": feed_url,
                    "artwork_url": r.get("artworkUrl100", ""),
                }
            )
        return podcasts

    except requests.RequestException:
        return []
