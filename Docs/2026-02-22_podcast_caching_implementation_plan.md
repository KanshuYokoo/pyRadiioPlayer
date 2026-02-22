# Podcast Episodes Caching Implementation Plan

## Goal Description
The user wants to save podcast episodes to a JSON format locally to quickly display the episodes list upon returning to a podcast, while continuing to fetch new episodes in the background to update the list and save new information.

## Proposed Changes

### Cache Mechanism
#### [NEW] app/models/podcast_cache.py
Create a `PodcastCache` class that handles saving and loading podcast data (info and episodes) to JSON files.
- Files will be saved in `~/.radio_player/podcasts/` using a hash of the feed URL as the filename.
- Implements a `save_and_merge` method which takes freshly fetched episodes and merges them with locally cached ones, using the `audio_url` as a unique identifier. This ensures that older episodes that drop off the RSS feed are still retained locally.

### UI Updates
#### [MODIFY] app/pages/podcast_page.py
- Import the new `PodcastCache` model.
- Modify `set_podcast` to first attempt loading from `PodcastCache` and populate the UI immediately if cached data exists.
- The background thread (`EpisodeFetchWorker`) will still run to fetch the latest feed.
- Update `_on_episodes_loaded` to call `PodcastCache.save_and_merge` with the newly fetched data. The UI will then be updated again with the merged list, adding any newly published episodes to the top of the list without losing cached history.

## Verification Plan

### Automated Tests
Run python format and lint tools.

### Manual Verification
1. Launch the application.
2. Select a podcast to load its episodes (this triggers a fetch and saves to cache).
3. Switch to another view and select the same podcast again. The episodes should load instantly from the JSON cache, and a background fetch should occur (showing an "Updating episodes..." indicator).
4. Inspect `~/.radio_player/podcasts/` and verify that a JSON file was created containing the podcast metadata and episode list.
