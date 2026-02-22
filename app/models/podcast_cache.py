"""Podcast caching and persistence."""

import json
import hashlib
from pathlib import Path
from typing import Tuple, List, Dict

CACHE_DIR = Path.home() / ".radio_player" / "podcasts"

class PodcastCache:
    @staticmethod
    def _ensure_dir():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def _get_file_path(feed_url: str) -> Path:
        url_hash = hashlib.md5(feed_url.encode('utf-8')).hexdigest()
        return CACHE_DIR / f"{url_hash}.json"
        
    @classmethod
    def load(cls, feed_url: str) -> Tuple[Dict, List[Dict]]:
        """Load cached info and episodes for a feed."""
        path = cls._get_file_path(feed_url)
        if not path.exists():
            return {}, []
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                info = data.get("info", {})
                episodes = data.get("episodes", [])
                return info, episodes
        except (json.JSONDecodeError, OSError):
            return {}, []

    @classmethod
    def save_and_merge(cls, feed_url: str, new_info: Dict, new_episodes: List[Dict]) -> Tuple[Dict, List[Dict]]:
        """Save new fetched data, merging with existing cached episodes.
        Returns the merged info and episodes.
        """
        cls._ensure_dir()
        path = cls._get_file_path(feed_url)
        
        info = {}
        merged_episodes = list(new_episodes)
        
        # Merge info
        existing_info, existing_episodes = cls.load(feed_url)
        info.update(existing_info)
        info.update({k: v for k, v in new_info.items() if v})
        
        # Merge episodes: keep order of new_episodes, then append older ones from cache
        existing_urls = {ep.get("audio_url") for ep in merged_episodes if ep.get("audio_url")}
        
        for ep in existing_episodes:
            url = ep.get("audio_url")
            if url and url not in existing_urls:
                merged_episodes.append(ep)
                existing_urls.add(url)
                
        data = {
            "info": info,
            "episodes": merged_episodes
        }
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass
            
        return info, merged_episodes
