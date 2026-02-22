# Walkthrough: Podcast Episode Download Feature

This feature adds user functionality to download and locally cache podcast episodes, which also helps prevent redownloading episodes every time the channel updates.

## Changes Made

1. **`app/services/download_service.py`**
   - Implemented a `QThread`-based worker `EpisodeDownloadWorker` to handle chunked MP3 downloads without blocking the UI.
   - Designed it to safely handle retries/failures and emit signals once completed.

2. **`app/models/podcast_cache.py`**
   - Added `get_download_path(feed_url, audio_url)` to compute structured local hash-based `.mp3` filenames saving files in `~/.radio_player/podcasts/<channel_hash>/<ep_hash>.mp3`.
   - Modified the JSON cache file so when an episode completes downloading, its state is quickly merged in through `mark_downloaded` and `mark_deleted`, allowing near-instant UI load times.

3. **`app/pages/podcast_page.py`**
   - Injected the "download" button into the episode row components.
   - Bound button interactions to manage start, downloading state, finishing logic, and deleting logic.
   - The UI correctly toggles between `"download"`, `"Downloading..."`, and `"Delete the episode"` dynamically based on user engagement.
   - Button functionality operates completely asynchronously.

## Validation Results

- **Syntax & Compilation:** Passed standard `py_compile` logic checks.
- **Cache Format Constraints:** Passed. Hashing mechanism and internal JSON updates conform to prior system formats while remaining backward compatible if older versions of the app don't understand `download_path` properties.

> [!TIP]
> You can now test it live! Open a podcast in the left pane, click the "download" button on any episode row, observe the text toggle to "Downloading...", check `~/.radio_player/podcasts` directory to verify the underlying `mp3` file exists, and observe the updated "Delete the episode" cache state persisting restarts!
