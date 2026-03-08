# CLAUDE.md — Internet Radio & Podcast Player

## Project Overview

A cross-platform desktop application for streaming internet radio stations and podcasts.
Built with **Python 3.9 + PySide6 (Qt 6)**. Originally developed with Google Gemini assistance.

**Run the app:**
```bash
python main.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
# Requirements: PySide6>=6.6, requests>=2.31, feedparser>=6.0
```

---

## Architecture

```
main.py                        # Entry point — QApplication + MainWindow
app/
  main_window.py               # QMainWindow: wires sidebar, pages, playback bar
  sidebar.py                   # Station list (260px fixed width), add/remove/search buttons
  playback_bar.py              # Bottom bar: QMediaPlayer + QAudioOutput, vol slider
  pages/
    station_page.py            # Radio station detail view (auto-plays on selection)
    podcast_page.py            # Podcast page: metadata + scrollable episode list
    search_page.py             # Search UI with tabbed radio/podcast results
  models/
    station.py                 # Station dataclass + StationManager (JSON persistence)
    podcast_cache.py           # PodcastCache: MD5-hashed JSON cache + download state
  services/
    radio_browser.py           # Radio Browser API (https://de1.api.radio-browser.info)
    itunes_search.py           # iTunes Search API (https://itunes.apple.com/search)
    feed_parser.py             # feedparser RSS parsing (episodes + feed metadata)
    download_service.py        # EpisodeDownloadWorker: streamed download via QThread
  dialogs/
    add_station.py             # AddStationDialog: name, URL, type (radio/podcast)
```

### Content stack indices (QStackedWidget)
| Index | Widget        |
|-------|---------------|
| 0     | Welcome page  |
| 1     | StationPage   |
| 2     | PodcastPage   |
| 3     | SearchPage    |

---

## Data Storage (`~/.radio_player/`)

| Path | Contents |
|------|----------|
| `stations.json` | Saved station/podcast list |
| `backup/stations_YYYYMMDD_HHMMSS.json` | Auto-backup created before any removal |
| `podcasts/<feed_md5>.json` | Cached podcast info + episode list (incl. `downloaded_path`) |
| `podcasts/<feed_md5>/<ep_md5>.mp3` | Downloaded episode audio files |

Station data file path is shown in **Help → Data Location** menu.

---

## Key Patterns & Conventions

### QThread Worker Safety (critical — do not break)
Workers emit a reference to themselves so Python's GC cannot destroy them mid-run:
```python
finished = Signal(object, list, str)   # (self, results, search_type)
self.finished.emit(self, results, self.search_type)
```
- `_active_workers: list` — holds hard references to all running workers
- `_current_worker` — tracks the latest request; stale results are discarded
- On completion: remove from `_active_workers`, call `worker.deleteLater()`

Documented in [Docs/Walkthrough_2026-02-22.md](Docs/Walkthrough_2026-02-22.md).

### Signal/Slot Wiring
All cross-widget communication uses PySide6 `Signal`/`Slot`. No direct widget-to-widget calls.
Key signals:
- `Sidebar.station_selected(int)` → `MainWindow._on_station_selected`
- `Sidebar.search_requested()` → show search page
- `Sidebar.remove_requested(int)` → confirmation dialog then remove
- `StationPage.play_requested(str, str)` → `PlaybackBar.play_url`
- `PodcastPage.play_requested(str, str)` → `PlaybackBar.play_url`
- `SearchPage.station_add_requested(str, str, str)` → `Sidebar.add_station_external`

### Station Types
`Station.station_type` is either `"radio"` or `"podcast"`.
- Radio → auto-plays on sidebar selection
- Podcast → loads PodcastPage, user manually plays episodes

### Podcast Cache Merge Strategy
`PodcastCache.save_and_merge()` keeps download state across refreshes:
1. Load existing cache (preserves `downloaded_path` fields)
2. New episodes from feed take precedence
3. Older cached episodes not in new feed are appended (preserves history)

### Button Signal Reconnection Pattern
When toggling download ↔ delete state on episode buttons:
```python
try:
    btn.clicked.disconnect()
except RuntimeError:
    pass
btn.clicked.connect(new_handler)
```

---

## External APIs

| Service | Endpoint | Used For |
|---------|----------|----------|
| Radio Browser | `https://de1.api.radio-browser.info/json/stations/byname/{q}` | Radio search, ordered by click count |
| iTunes Search | `https://itunes.apple.com/search?media=podcast` | Podcast search |
| RSS/feedparser | Any RSS/Atom feed URL | Podcast episode listing |

All network calls run in `QThread` workers — never on the main/UI thread.

---

## Development Docs

All implementation history in [Docs/](Docs/):
- `Walkthrough_2026-02-22.md` — QThread crash fix (GC / worker lifecycle)
- `2026-02-22_podcast_caching_implementation_plan.md` — podcast cache design
- `2026-02-22_podcast_caching_walkthrough.md` — cache implementation walkthrough
- `2026-02-22_new_station_removal_workflow_plan.md` — removal + backup workflow
- `2026-02-22_new_station_removal_workflow_walkthrough.md`
- `2026-02-22_podcast_episode_download_feature_plan.md` — episode download design
- `2026-02-22_podcast_episode_download_walkthrough.md`

---

## Known Issues / Watch Points

1. **`_stop()` is called directly on `PlaybackBar`** from `MainWindow._on_station_remove_requested` — this bypasses the public `play_url` API; consider exposing a `stop()` method.
2. **`feed_parser.py` ignores the `timeout` parameter** — `feedparser.parse()` does not accept a timeout kwarg; the default HTTP timeout applies.
3. **Download extension hardcoded to `.mp3`** — `PodcastCache.get_download_path()` always uses `.mp3` regardless of actual audio format.
4. **No URL validation** in `AddStationDialog._on_accept()` — only checks non-empty.
5. **`EpisodeFetchWorker` calls `feedparser.parse()` twice** (once in `fetch_feed_info`, once in `fetch_episodes`) for every podcast load — wasteful network/parse overhead.
6. **`SearchWorker` class-level `Signal` import** uses a local alias `_Signal` which is unconventional — works but looks odd.
