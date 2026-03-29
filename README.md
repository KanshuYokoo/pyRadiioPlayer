# PySide6 Radio Player

## What Was Built

A cross-platform internet radio & podcast player using **Python + PySide6 (Qt 6)**. Runs natively on macOS and Linux from the same codebase.

## Project Structure

```
newproject/
├── main.py                     ← Entry point
├── requirements.txt
├── app/
│   ├── main_window.py          ← Main window + Help menu
│   ├── sidebar.py              ← Station list + add/remove
│   ├── playback_bar.py         ← Play/pause/stop + volume
│   ├── dialogs/
│   │   └── add_station.py      ← Add station popup
│   ├── pages/
│   │   ├── station_page.py     ← Radio station detail
│   │   ├── podcast_page.py     ← Podcast + episode list
│   │   └── search_page.py      ← Radio/podcast search
│   ├── models/
│   │   └── station.py          ← Data model + JSON persistence
│   └── services/
│       ├── radio_browser.py    ← Radio Browser API
│       ├── itunes_search.py    ← iTunes podcast search
│       └── feed_parser.py      ← RSS episode parser
```

## Key Features

| Feature | Implementation |
|---------|---------------|
| **Station list** | Sidebar with 📻/🎙 icons, click to play |
| **Add station** | "+" button → dialog with name, URL, type fields |
| **Remove station** | "−" button → trash icon mode, click to delete |
| **Playback** | QMediaPlayer with play/pause/stop + volume slider |
| **Radio search** | Radio Browser API (sorted by popularity) |
| **Podcast search** | iTunes Search API |
| **Episode list** | RSS feed parsing with background loading |
| **Persistence** | JSON file at `~/.radio_player/stations.json` |
| **Help menu** | About dialog + Data Location dialog |
| **Theme** | System default (native look on macOS/Linux) |

## How to Run

```bash
cd /Users/yokookanshu/work/newproject
source venv/bin/activate
python main.py
```

## Building a Standalone Executable (PyInstaller)

Install PyInstaller (already in `requirements.txt`):

```bash
pip install pyinstaller
```

Build using the spec file:

```bash
pyinstaller main.spec
```

Output in `dist/`:
- `pyRadioTunes` — Unix binary, runnable from terminal
- `pyRadioTunes.app` — macOS double-clickable app bundle

### Renaming the executable

Edit these two lines in `main.spec`:

```python
# In the EXE block:
name='pyRadioTunes',

# In the BUNDLE block:
name='pyRadioTunes.app',
```

Change both to your preferred name, then rebuild with `pyinstaller main.spec`.

> **Note:** PyInstaller builds for the OS it runs on. Run it separately on macOS, Linux, and Windows to get platform-specific outputs.

---

## Verification Results

- ✅ Virtual environment created with Python 3.9
- ✅ All dependencies installed (PySide6 6.10.2, requests 2.32.5, feedparser 6.0.12)
- ✅ All 12 modules import without errors
- ⏳ Manual UI testing pending (launch, playback, search, add/remove)
