# Walkthrough: New Station Removal Workflow

This walkthrough details the changes made to replace the `-` (Remove) button's toggling behavior with an immediate, confirmation-based removal workflow that also stops active playback and creates a backup of your stations list.

## Changes Made

1. **`app/models/station.py`**
   - Added `backup_stations()` logic to use `shutil.copy2` to copy the `stations.json` into `~/.radio_player/backup/stations_YYYYMMDD_HHMMSS.json` right before a deletion occurs.

2. **`app/sidebar.py`**
   - Removed the "removal mode" state entirely.
   - The `-` button now immediately looks at the currently highlighted channel in the sidebar (`self.list_widget.currentRow()`).
   - If a valid channel is selected, it emits a newly added `remove_requested` signal.

3. **`app/main_window.py`**
   - Wired up the `remove_requested` signal to a new confirmation flow.
   - When triggered, a `QMessageBox.question` dialog asks the user: "Are you sure you want to remove '[station name]'?".
   - Upon confirming "Yes":
     1. `self.playback_bar._stop()` is called to immediately halt any stream playing.
     2. `self.station_manager.backup_stations()` triggers the timestamped JSON backup.
     3. `self.station_manager.remove_station(index)` removes the channel from the active model.
     4. `self.sidebar.refresh()` updates the UI to reflect the removal.

## Validation Results
- Code passed syntax checks.
- Workflow tested sequentially to confirm prompt appearance, backup generation, stoppage of audio playback, and definitive channel removal.

> [!TIP]
> Try it out! Select a station, make sure it is playing, and click `-`. Click `Yes` on the prompt. The audio will stop, the station will disappear, and you can navigate to `~/.radio_player/backup/` to see your timestamped JSON backups!
