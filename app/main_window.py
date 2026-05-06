"""Main window — assembles sidebar, content pages, and playback bar."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QStackedWidget,
    QLabel,
    QMenuBar,
    QMessageBox,
    QPushButton,
)
from PySide6.QtCore import Qt, Slot

from app.models.station import Station, StationManager
from app.sidebar import Sidebar
from app.playback_bar import PlaybackBar
from app.pages.station_page import StationPage
from app.pages.podcast_page import PodcastPage
from app.pages.search_page import SearchPage


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Player")
        self.setMinimumSize(900, 600)
        self.resize(1000, 680)

        # Data
        self.station_manager = StationManager()
        self._current_station_index: int | None = None

        # Setup
        self._setup_menubar()
        self._setup_ui()
        self._connect_signals()

    def _setup_menubar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&Quit", self.close)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&About", self._show_about)
        help_menu.addAction("Data &Location", self._show_data_location)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top area: sidebar + content
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self.station_manager)
        content_layout.addWidget(self.sidebar)

        # Right panel: top bar + content stack
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top bar with "Show Now Playing" button (right-aligned)
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(8, 6, 8, 6)
        top_bar_layout.addStretch()
        self.now_playing_btn = QPushButton("Show Now Playing")
        self.now_playing_btn.setFixedHeight(28)
        self.now_playing_btn.setToolTip("Return to the currently playing station")
        self.now_playing_btn.setEnabled(False)
        self.now_playing_btn.clicked.connect(self._on_now_playing_requested)
        top_bar_layout.addWidget(self.now_playing_btn)
        right_layout.addWidget(top_bar)

        # Content stack
        self.content_stack = QStackedWidget()

        # Welcome page (index 0)
        welcome = QWidget()
        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.addStretch()
        welcome_label = QLabel("🎵 Welcome to Radio Player")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: gray;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        subtitle = QLabel("Select a station from the sidebar, or search for new ones")
        subtitle.setStyleSheet("font-size: 14px; color: gray;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(subtitle)
        welcome_layout.addStretch()
        self.content_stack.addWidget(welcome)  # index 0

        # Station page (index 1)
        self.station_page = StationPage()
        self.content_stack.addWidget(self.station_page)  # index 1

        # Podcast page (index 2)
        self.podcast_page = PodcastPage()
        self.content_stack.addWidget(self.podcast_page)  # index 2

        # Search page (index 3)
        self.search_page = SearchPage()
        self.content_stack.addWidget(self.search_page)  # index 3

        right_layout.addWidget(self.content_stack, stretch=1)
        content_layout.addWidget(right_panel, stretch=1)

        main_layout.addWidget(content_area, stretch=1)

        # Playback bar at bottom
        self.playback_bar = PlaybackBar()
        main_layout.addWidget(self.playback_bar)

    def _connect_signals(self):
        # Sidebar
        self.sidebar.station_selected.connect(self._on_station_selected)
        self.sidebar.search_requested.connect(self._show_search)
        self.sidebar.remove_requested.connect(self._on_station_remove_requested)

        # Station page
        self.station_page.play_requested.connect(self._play_stream)

        # Podcast page
        self.podcast_page.play_requested.connect(self._play_stream)

        # Search page
        self.search_page.station_add_requested.connect(self._on_search_add)

    @Slot(int)
    def _on_station_selected(self, index: int):
        station = self.station_manager.get_station(index)
        if not station:
            return

        self._current_station_index = index
        self.now_playing_btn.setEnabled(True)

        if station.station_type == "podcast":
            self.podcast_page.set_podcast(station.name, station.url)
            self.content_stack.setCurrentIndex(2)
        else:
            self.station_page.set_station(station.name, station.url)
            self.content_stack.setCurrentIndex(1)
            # Auto-play radio stations
            self._play_stream(station.url, station.name)

    @Slot()
    def _on_now_playing_requested(self):
        if self._current_station_index is None:
            return
        station = self.station_manager.get_station(self._current_station_index)
        if not station:
            return
        self.sidebar.select_row(self._current_station_index)
        if station.station_type == "podcast":
            self.content_stack.setCurrentIndex(2)
        else:
            self.content_stack.setCurrentIndex(1)

    @Slot(int)
    def _on_station_remove_requested(self, index: int):
        station = self.station_manager.get_station(index)
        if not station:
            return

        reply = QMessageBox.question(
            self,
            "Remove Station",
            f"Are you sure you want to remove '{station.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Stop playback
            self.playback_bar.stop()
            # Backup
            self.station_manager.backup_stations()
            # Remove
            self.station_manager.remove_station(index)
            # Refresh Sidebar UI
            self.sidebar.refresh()
            # Update current station tracking
            if self._current_station_index is not None:
                if index == self._current_station_index:
                    self._current_station_index = None
                    self.now_playing_btn.setEnabled(False)
                    self.content_stack.setCurrentIndex(0)
                elif index < self._current_station_index:
                    self._current_station_index -= 1

    @Slot()
    def _show_search(self):
        self.content_stack.setCurrentIndex(3)

    @Slot(str, str)
    def _play_stream(self, url: str, name: str):
        self.playback_bar.play_url(url, name)

    @Slot(str, str, str)
    def _on_search_add(self, name: str, url: str, stype: str):
        station = Station(name=name, url=url, station_type=stype)
        self.sidebar.add_station_external(station)

    def _show_about(self):
        QMessageBox.about(
            self,
            "About Radio Player",
            "<h3>Radio Player</h3>"
            "<p>A cross-platform internet radio &amp; podcast player.</p>"
            "<p>Built with Python + PySide6 (Qt 6).</p>"
            "<p>Radio search powered by Radio Browser API.<br>"
            "Podcast search powered by iTunes Search API.</p>",
        )

    def _show_data_location(self):
        path = self.station_manager.get_data_path()
        QMessageBox.information(
            self,
            "Data Location",
            f"<p>Your saved stations are stored at:</p>"
            f"<p><b>{path}</b></p>"
            f"<p>You can back up or edit this file manually.</p>",
        )
