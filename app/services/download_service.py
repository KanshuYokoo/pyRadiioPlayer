"""Service for downloading podcast episodes."""

import os
import requests
from pathlib import Path
from PySide6.QtCore import QThread, Signal

class EpisodeDownloadWorker(QThread):
    """Background thread to download an audio file."""
    
    # Emits (success, file_path, error_message)
    finished_download = Signal(bool, str, str)

    def __init__(self, audio_url: str, destination_path: Path, parent=None):
        super().__init__(parent)
        self.audio_url = audio_url
        self.destination_path = destination_path

    def run(self):
        try:
            # Ensure the parent directory exists
            self.destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use a stream to safely download large files without memory overload
            with requests.get(self.audio_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(self.destination_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            
            self.finished_download.emit(True, str(self.destination_path), "")
        except Exception as e:
            # Clean up partial file on failure
            if self.destination_path.exists():
                try:
                    os.remove(self.destination_path)
                except OSError:
                    pass
            self.finished_download.emit(False, "", str(e))
