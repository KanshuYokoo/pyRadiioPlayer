# Podcast Episode Download Feature Plan

This plan describes how to add a capability to download an individual podcast episode and later delete it.

## User Review Required
No major UI breaking changes, just adding a button per episode row. We will create a `downloads/podcasts` subfolder in the `~/.radio_player` directory to store the MP3s securely. Does that sound good? 

## Proposed Changes

### app/models

#### [MODIFY] podcast_cache.py
* Add a helper `get_download_path(feed_url: str, audio_url: str) -> Path` to calculate the persistent storage path, utilizing hashing to ensure safe filenames.
* Add class methods `mark_downloaded(feed_url, audio_url, path)` and `mark_deleted(feed_url, audio_url)` which load the JSON cache, iterate over episodes to find the matching `audio_url`, update the `downloaded_path` key, and rewrite the JSON. This satisfies the "quick load" requirement.

---

### app/services

#### [NEW] download_service.py
* Create `EpisodeDownloadWorker(QThread)` to handle non-blocking asynchronous downloads.
* It will take the remote `audio_url` and a target local `destination_path`. 
* Uses the existing `requests` dependency to download the audio content iteratively, then emit a `finished(success: bool)` signal.

---

### app/pages

#### [MODIFY] podcast_page.py
* In `_add_episode_row`, inspect `ep.get("downloaded_path")`. Check if the file actually exists on the disk.
* Render a new `QPushButton`. If downloaded, the text will be `"Delete the episode"`. Otherwise, `"download"`.
* Connect the button to slots `_start_download(audio_url, feed_url, btn)` or `_delete_download(audio_url, feed_url, btn)` that handle the logic:
  * Downloading initiates the `EpisodeDownloadWorker`. When finished, calls `PodcastCache.mark_downloaded` and updates the button text.
  * Deleting removes the file using `os.remove` or `Path.unlink`, calls `PodcastCache.mark_deleted`, and updates the button text to `"download"`.
* Add visual feedback during download (e.g. text changing to `"Downloading..."` and disabling the button momentarily).

## Verification Plan

### Automated Tests
* None existing (assuming standard PyQt logic applies - no tests were found in the `app` struct).

### Manual Verification
1. Open the application.
2. Select a podcast in the sidebar. 
3. Scroll through episodes; click the "download" button.
4. Verify the button changes to "Downloading..." and when complete, "Delete the episode".
5. Close the app and reopen it, verify the list is loaded with the latest state correctly reflecting "Delete the episode" in an instant because of the updated `.json` cache.
6. Check `~/.radio_player/downloads/podcasts/` locally to ensure the `.mp3` file was saved.
7. Click "Delete the episode" and verify the file is removed and UI changes back to "download".
