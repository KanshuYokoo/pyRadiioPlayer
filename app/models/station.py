"""Station and podcast data model with JSON persistence."""

import json
import os
import shutil
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


DATA_DIR = Path.home() / ".radio_player"
STATIONS_FILE = DATA_DIR / "stations.json"

DEFAULT_STATIONS = [
    {
        "name": "Jazz Radio",
        "url": "http://stream.radioparadise.com/aac-320",
        "station_type": "radio",
        "favicon_url": "",
    },
    {
        "name": "Classical KUSC",
        "url": "https://kusc.streamguys1.com/kusc-128k-mp3",
        "station_type": "radio",
        "favicon_url": "",
    },
    {
        "name": "BBC World Service",
        "url": "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
        "station_type": "radio",
        "favicon_url": "",
    },
    {
        "name": "SomaFM Groove Salad",
        "url": "https://ice1.somafm.com/groovesalad-256-mp3",
        "station_type": "radio",
        "favicon_url": "",
    },
]


@dataclass
class Station:
    """Represents a radio station or podcast."""

    name: str
    url: str
    station_type: str = "radio"  # "radio" or "podcast"
    favicon_url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Station":
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            station_type=data.get("station_type", "radio"),
            favicon_url=data.get("favicon_url", ""),
        )


class StationManager:
    """Manages station list with JSON file persistence."""

    def __init__(self):
        self._stations: list[Station] = []
        self._ensure_data_dir()
        self.load()

    @staticmethod
    def get_data_path() -> str:
        """Return the path to the stations data file."""
        return str(STATIONS_FILE)

    def _ensure_data_dir(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load(self):
        """Load stations from JSON file, or create defaults if none exist."""
        if STATIONS_FILE.exists():
            try:
                with open(STATIONS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._stations = [Station.from_dict(s) for s in data]
            except (json.JSONDecodeError, KeyError):
                self._stations = self._create_defaults()
                self.save()
        else:
            self._stations = self._create_defaults()
            self.save()

    def _create_defaults(self) -> list[Station]:
        return [Station.from_dict(s) for s in DEFAULT_STATIONS]

    def save(self):
        """Persist stations to JSON file."""
        self._ensure_data_dir()
        with open(STATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self._stations], f, indent=2)

    @property
    def stations(self) -> list[Station]:
        return list(self._stations)

    def add_station(self, station: Station):
        """Add a station and save."""
        self._stations.append(station)
        self.save()

    def backup_stations(self):
        """Backup stations.json to a timestamped file."""
        if not STATIONS_FILE.exists():
            return
            
        backup_dir = DATA_DIR / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"stations_{timestamp}.json"
        
        try:
            shutil.copy2(STATIONS_FILE, backup_dir / backup_filename)
        except OSError as e:
            print(f"Failed to backup stations.json: {e}")

    def remove_station(self, index: int):
        """Remove station by index and save."""
        if 0 <= index < len(self._stations):
            self._stations.pop(index)
            self.save()

    def get_station(self, index: int) -> Optional[Station]:
        if 0 <= index < len(self._stations):
            return self._stations[index]
        return None
