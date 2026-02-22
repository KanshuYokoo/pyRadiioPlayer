# Implementation Plan: New Station Removal Workflow

## Proposed Changes

### 1. `app/models/station.py`
**[MODIFY] StationManager**
- Import `shutil` and `datetime`.
- Add a new method `backup_stations(self)`.
- The method will check if `stations.json` exists, create a `.radio_player/backup/` directory if it doesn't exist, and copy the current `stations.json` into it with a timestamp `stations_YYYYMMDD_HHMMSS.json`.

---

### 2. `app/sidebar.py`
**[MODIFY] Sidebar**
- Remove all state and logic related to `_remove_mode` (including `self._remove_mode`, `self._toggle_remove_mode()`, `self.mode_label`, and the conditional rendering in `_refresh_list()`).
- The list widget will now behave strictly as a selection list.
- Add a new signal `remove_requested = Signal(int)` that emits the index of the station to be removed.
- Modify the `-` button handler `self.remove_btn.clicked.connect(self._on_remove_clicked)` to check the currently selected row (`self.list_widget.currentRow()`) and emit the `remove_requested` signal with that row index if $\ge 0$. If no row is selected, it can show a quick warning or do nothing.

---

### 3. `app/main_window.py`
**[MODIFY] MainWindow**
- Connect `self.sidebar.remove_requested.connect(self._on_station_remove_requested)`.
- Implement `_on_station_remove_requested(self, index: int)`:
  1. Retrieve the `Station` object.
  2. Show a `QMessageBox.question` with "Are you sure you want to remove '[Station Name]'?".
  3. If the user clicks `Yes`:
     - Stop playback using `self.playback_bar._stop()`.
     - Backup the JSON file calling `self.station_manager.backup_stations()`.
     - Remove the station calling `self.station_manager.remove_station(index)`.
     - Refresh the sidebar `self.sidebar.refresh()`.

## Verification Plan
1. Open the application.
2. Select a currently available station to verify playback starts.
3. Click the `-` button. A dialog should appear asking for confirmation to remove the channel.
4. Click `No`. The playback should continue and the channel should remain.
5. Click the `-` button again and click `Yes`.
6. Verify the audio stops.
7. Verify the channel is removed from the sidebar.
8. Check `~/.radio_player/backup/` to verify a timestamped `.json` file was created and contains the data from immediately *before* the removal.
