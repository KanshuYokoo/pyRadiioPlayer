"""Search page — search for radio stations and podcasts online."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QThread, Slot

from app.services.radio_browser import search_stations
from app.services.itunes_search import search_podcasts


class SearchWorker(QThread):
    """Background thread for search queries."""

    from PySide6.QtCore import Signal as _Signal

    finished = _Signal(list, str)  # results, search_type

    def __init__(self, query: str, search_type: str, parent=None):
        super().__init__(parent)
        self.query = query
        self.search_type = search_type

    def run(self):
        if self.search_type == "radio":
            results = search_stations(self.query)
        else:
            results = search_podcasts(self.query)
        self.finished.emit(results, self.search_type)


class SearchPage(QWidget):
    """Search for radio stations (Radio Browser) and podcasts (iTunes)."""

    station_add_requested = Signal(str, str, str)  # name, url, type

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        # Header
        header = QLabel("🔍 Find Stations & Podcasts")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name…")
        self.search_input.setFixedHeight(36)
        self.search_input.returnPressed.connect(self._do_search)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Search")
        self.search_btn.setFixedHeight(36)
        self.search_btn.clicked.connect(self._do_search)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Radio tab
        self.radio_scroll = QScrollArea()
        self.radio_scroll.setWidgetResizable(True)
        self.radio_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.radio_container = QWidget()
        self.radio_layout = QVBoxLayout(self.radio_container)
        self.radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_layout.setSpacing(4)
        self.radio_layout.addStretch()
        self.radio_scroll.setWidget(self.radio_container)
        self.tabs.addTab(self.radio_scroll, "📻 Radio Stations")

        # Podcast tab
        self.podcast_scroll = QScrollArea()
        self.podcast_scroll.setWidgetResizable(True)
        self.podcast_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.podcast_container = QWidget()
        self.podcast_layout = QVBoxLayout(self.podcast_container)
        self.podcast_layout.setContentsMargins(0, 0, 0, 0)
        self.podcast_layout.setSpacing(4)
        self.podcast_layout.addStretch()
        self.podcast_scroll.setWidget(self.podcast_container)
        self.tabs.addTab(self.podcast_scroll, "🎙 Podcasts")

        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

    def _do_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        search_type = "radio" if self.tabs.currentIndex() == 0 else "podcast"
        self.status_label.setText(f"Searching {search_type}s for \"{query}\"…")
        self.search_btn.setEnabled(False)

        self._worker = SearchWorker(query, search_type)
        self._worker.finished.connect(self._on_results)
        self._worker.start()

    @Slot(list, str)
    def _on_results(self, results: list, search_type: str):
        self.search_btn.setEnabled(True)

        if search_type == "radio":
            self._populate_radio_results(results)
        else:
            self._populate_podcast_results(results)

        if not results:
            self.status_label.setText("No results found.")
        else:
            self.status_label.setText(f"Found {len(results)} results")

    def _populate_radio_results(self, results: list):
        self._clear_layout(self.radio_layout)

        for r in results:
            row = QFrame()
            row.setFrameShape(QFrame.Shape.StyledPanel)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 8, 10, 8)
            row_layout.setSpacing(12)

            # Info
            info_layout = QVBoxLayout()
            name_lbl = QLabel(r["name"])
            name_lbl.setStyleSheet("font-size: 13px; font-weight: 600;")
            name_lbl.setWordWrap(True)
            info_layout.addWidget(name_lbl)

            meta_parts = []
            if r.get("country"):
                meta_parts.append(r["country"])
            if r.get("tags"):
                meta_parts.append(r["tags"][:60])
            if r.get("bitrate"):
                meta_parts.append(f"{r['bitrate']} kbps")
            if meta_parts:
                meta_lbl = QLabel(" · ".join(meta_parts))
                meta_lbl.setStyleSheet("font-size: 11px; color: gray;")
                meta_lbl.setWordWrap(True)
                info_layout.addWidget(meta_lbl)

            row_layout.addLayout(info_layout, stretch=1)

            # Add button
            add_btn = QPushButton("+ Add")
            add_btn.setFixedSize(70, 32)
            name = r["name"]
            url = r["url"]
            add_btn.clicked.connect(
                lambda checked, n=name, u=url: self._add_station(n, u, "radio", add_btn)
            )
            row_layout.addWidget(add_btn)

            count = self.radio_layout.count()
            self.radio_layout.insertWidget(count - 1, row)

    def _populate_podcast_results(self, results: list):
        self._clear_layout(self.podcast_layout)

        for r in results:
            row = QFrame()
            row.setFrameShape(QFrame.Shape.StyledPanel)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 8, 10, 8)
            row_layout.setSpacing(12)

            # Info
            info_layout = QVBoxLayout()
            name_lbl = QLabel(r["name"])
            name_lbl.setStyleSheet("font-size: 13px; font-weight: 600;")
            name_lbl.setWordWrap(True)
            info_layout.addWidget(name_lbl)

            if r.get("artist"):
                artist_lbl = QLabel(r["artist"])
                artist_lbl.setStyleSheet("font-size: 11px; color: gray;")
                info_layout.addWidget(artist_lbl)

            row_layout.addLayout(info_layout, stretch=1)

            # Add button
            add_btn = QPushButton("+ Add")
            add_btn.setFixedSize(70, 32)
            name = r["name"]
            url = r["feed_url"]
            add_btn.clicked.connect(
                lambda checked, n=name, u=url: self._add_station(n, u, "podcast", add_btn)
            )
            row_layout.addWidget(add_btn)

            count = self.podcast_layout.count()
            self.podcast_layout.insertWidget(count - 1, row)

    def _add_station(self, name: str, url: str, stype: str, btn: QPushButton):
        self.station_add_requested.emit(name, url, stype)
        btn.setText("✓ Added")
        btn.setEnabled(False)

    @staticmethod
    def _clear_layout(layout):
        while layout.count() > 1:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
