"""Sidebar — station list with add/remove controls and search button."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QIcon

from app.models.station import Station, StationManager
from app.dialogs.add_station import AddStationDialog


class Sidebar(QWidget):
    """Sidebar showing saved stations with add/remove/search buttons."""

    station_selected = Signal(int)  # index of selected station
    search_requested = Signal()
    remove_requested = Signal(int)  # index of station to remove

    def __init__(self, station_manager: StationManager, parent=None):
        super().__init__(parent)
        self.station_manager = station_manager
        self.setFixedWidth(260)
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 8, 8)

        title = QLabel("Stations")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Search button
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(32, 32)
        self.search_btn.setToolTip("Find stations & podcasts")
        self.search_btn.clicked.connect(self.search_requested.emit)
        header_layout.addWidget(self.search_btn)

        # Add button (top-right)
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(32, 32)
        self.add_btn.setToolTip("Add station")
        self.add_btn.setStyleSheet("QPushButton { font-size: 18px; font-weight: bold; }")
        self.add_btn.clicked.connect(self._on_add)
        header_layout.addWidget(self.add_btn)

        layout.addWidget(header)

        # Station list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        layout.addWidget(self.list_widget)

        # Bottom bar
        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(8, 4, 8, 8)

        # Remove button (bottom-left)
        self.remove_btn = QPushButton("−")
        self.remove_btn.setFixedSize(32, 32)
        self.remove_btn.setToolTip("Remove selected station")
        self.remove_btn.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        bottom_layout.addWidget(self.remove_btn)

        bottom_layout.addStretch()
        layout.addWidget(bottom)

    def _refresh_list(self):
        """Rebuild the list widget from the station manager."""
        old_state = self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for station in self.station_manager.stations:
            icon = "🎙" if station.station_type == "podcast" else "📻"
            item_text = f"{icon}  {station.name}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, station)
            self.list_widget.addItem(item)
            
        self.list_widget.blockSignals(old_state)

    @Slot()
    def _on_add(self):
        dialog = AddStationDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            station = Station(
                name=data["name"],
                url=data["url"],
                station_type=data["station_type"],
            )
            self.station_manager.add_station(station)
            self._refresh_list()

    @Slot()
    def _on_remove_clicked(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.remove_requested.emit(row)

    @Slot(int)
    def _on_selection_changed(self, row: int):
        if row < 0:
            return
            
        self.station_selected.emit(row)

    def select_row(self, index: int):
        """Highlight a row in the list without emitting station_selected."""
        old_state = self.list_widget.blockSignals(True)
        self.list_widget.setCurrentRow(index)
        self.list_widget.blockSignals(old_state)

    def add_station_external(self, station: Station):
        """Add a station from external source (e.g. search page)."""
        self.station_manager.add_station(station)
        self._refresh_list()

    def refresh(self):
        """Public refresh for external updates."""
        self._refresh_list()
