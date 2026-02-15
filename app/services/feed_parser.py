"""RSS feed parser for podcast episode listings."""

import feedparser
from typing import Optional


def fetch_episodes(feed_url: str, timeout: int = 15) -> list[dict]:
    """Parse a podcast RSS feed and return a list of episodes.

    Returns a list of dicts with keys: title, published, audio_url, duration, description.
    """
    try:
        feed = feedparser.parse(feed_url)
    except Exception:
        return []

    episodes = []
    for entry in feed.entries:
        # Find the audio enclosure
        audio_url = ""
        for link in entry.get("links", []):
            if link.get("type", "").startswith("audio/") or link.get("rel") == "enclosure":
                audio_url = link.get("href", "")
                break
        # Also check enclosures list
        if not audio_url:
            for enc in entry.get("enclosures", []):
                if enc.get("type", "").startswith("audio/"):
                    audio_url = enc.get("href", "")
                    break

        if not audio_url:
            continue

        # Duration in itunes:duration tag
        duration = entry.get("itunes_duration", "")

        episodes.append(
            {
                "title": entry.get("title", "Untitled"),
                "published": entry.get("published", ""),
                "audio_url": audio_url,
                "duration": duration,
                "description": entry.get("summary", ""),
            }
        )

    return episodes


def fetch_feed_info(feed_url: str) -> dict:
    """Fetch podcast metadata from an RSS feed.

    Returns dict with keys: title, description, image_url.
    """
    try:
        feed = feedparser.parse(feed_url)
    except Exception:
        return {"title": "", "description": "", "image_url": ""}

    feed_info = feed.get("feed", {})
    image_url = ""
    if "image" in feed_info and "href" in feed_info["image"]:
        image_url = feed_info["image"]["href"]
    # itunes image
    if not image_url:
        itunes_image = feed_info.get("itunes_image", {})
        if isinstance(itunes_image, dict):
            image_url = itunes_image.get("href", "")

    return {
        "title": feed_info.get("title", ""),
        "description": feed_info.get("subtitle", feed_info.get("summary", "")),
        "image_url": image_url,
    }
