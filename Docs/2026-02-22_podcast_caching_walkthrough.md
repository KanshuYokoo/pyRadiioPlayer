# Podcast Episodes Caching Implementation

## Changes Made
- **Created PodcastCache Model (`app/models/podcast_cache.py`)**: A new data class that handles caching podcast info and episodes to local `.json` files within `~/.radio_player/podcasts/`. It maps a feed URL to a file using an MD5 hash.
- **Merge Logic**: Implemented `PodcastCache.save_and_merge()`, which combines newly fetched episodes from the RSS feed with the locally cached episodes, utilizing `audio_url` as a unique identifier. This ensures older episodes that might age out of the RSS feed are retained in the local JSON cache.
- **Updated Podcast Page (`app/pages/podcast_page.py`)**:
    - Altered `set_podcast` to immediately load and display data from `PodcastCache` if available, preventing the "Loading episodes..." screen if the cache exists. Wait times are significantly reduced.
    - Added UI updates to reflect when the app displays cached items and when it fetches backgrounds ("Updating episodes...").
    - The background feed fetch still occurs seamlessly. Once completed, `_on_episodes_loaded` merges the new fetch into cache, and the UI re-renders with the freshest data on top.

## Validation Results
- Python syntax validations ran completely without errors.
- Confirmed saving locations and dict mappings logic inside the caching model.

## Action Required
Please launch the application and open a podcast. Switch views and return to evaluate the speed of loading. Check the disk at `~/.radio_player/podcasts/` to inspect the generated JSON files holding the episodes list.
