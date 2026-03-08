"""RSS feed parser for podcast episode listings."""

import feedparser


def fetch_feed(feed_url: str) -> tuple[dict, list[dict]]:
    """Parse a podcast RSS feed once and return (info, episodes).

    info keys: title, description, image_url
    episode keys: title, published, audio_url, duration, description
    """
    try:
        feed = feedparser.parse(feed_url)
    except Exception:
        return {"title": "", "description": "", "image_url": ""}, []

    info = _extract_info(feed)
    episodes = _extract_episodes(feed)
    return info, episodes


def _extract_info(feed) -> dict:
    feed_info = feed.get("feed", {})
    image_url = ""
    if "image" in feed_info and "href" in feed_info["image"]:
        image_url = feed_info["image"]["href"]
    if not image_url:
        itunes_image = feed_info.get("itunes_image", {})
        if isinstance(itunes_image, dict):
            image_url = itunes_image.get("href", "")

    return {
        "title": feed_info.get("title", ""),
        "description": feed_info.get("subtitle", feed_info.get("summary", "")),
        "image_url": image_url,
    }


def _extract_episodes(feed) -> list[dict]:
    episodes = []
    for entry in feed.entries:
        audio_url = ""
        for link in entry.get("links", []):
            if link.get("type", "").startswith("audio/") or link.get("rel") == "enclosure":
                audio_url = link.get("href", "")
                break
        if not audio_url:
            for enc in entry.get("enclosures", []):
                if enc.get("type", "").startswith("audio/"):
                    audio_url = enc.get("href", "")
                    break

        if not audio_url:
            continue

        episodes.append(
            {
                "title": entry.get("title", "Untitled"),
                "published": entry.get("published", ""),
                "audio_url": audio_url,
                "duration": entry.get("itunes_duration", ""),
                "description": entry.get("summary", ""),
            }
        )

    return episodes
