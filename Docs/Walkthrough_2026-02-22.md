# Fix QThread Crash Walkthrough

## Issue 
The application was crashing randomly when interacting with the search page or clicking on podcasts. The crash resulted in: `QThread: Destroyed while thread '' is still running`.

This occurred because the `QThread` workers used for network requests were stored in a single variable (`self._worker`). Subsequent clicks or queries replaced the object reference, causing Python's garbage collector to destroy the old worker object before the C++ thread finished its execution.

## Changes Made

### 1. `SearchPage` (`app/pages/search_page.py`)
- Refactored `SearchWorker` to emit a reference to itself upon completion: `finished = Signal(object, list, str)`.
- Introduced `self._active_workers` list to hold robust references to all currently executing threads.
- Added `self._current_worker` to keep track of the most recent request.
- Implemented a slot `_on_results` that:
  - Takes the `worker` reference, removes it from `_active_workers`, and safely calls `worker.deleteLater()`.
  - Aborts UI updates if the worker is not the current worker, ensuring old search results do not overwrite newer ones.

### 2. `PodcastPage` (`app/pages/podcast_page.py`)
- Refactored `EpisodeFetchWorker` to emit a reference to itself upon completion: `finished = Signal(object, list, dict)`.
- Addressed garbage collection identically to `SearchPage` using `self._active_workers` and `self._current_worker`.
- Implemented `_on_episodes_loaded` to handle the safe removal, deletion, and selective UI updating.

## Validation Results

The QThread instances are now retained accurately throughout their execution lifespan and properly deleted upon finishing. 

### Recommended Manual Verification

Please launch the app by running `python main.py` and verify:
1. Navigating to the **Search Page** and pressing `Enter` multiple times quickly to trigger multiple search queries. The program should not crash, and the UI should only display results for the latest query.
2. Interacting with the **Podcast Page** by rapidly clicking on multiple saved podcasts in the sidebar back-and-forth. The app should stay stable and properly render the episodes of the last clicked podcast.
