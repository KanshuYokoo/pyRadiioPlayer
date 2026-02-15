"""Station detail page — shown when a radio station is selected."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class StationPage(QWidget):
    """Displays info for a radio station and a large play button."""

    play_requested = Signal(str, str)  # url, station_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        # Station name
        self.name_label = QLabel("Select a station")
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.name_label)

        # Type badge
        self.type_label = QLabel("📻 Radio Station")
        self.type_label.setStyleSheet("font-size: 13px; color: gray;")
        layout.addWidget(self.type_label)

        # URL display
        self.url_label = QLabel("")
        self.url_label.setStyleSheet("font-size: 12px; color: gray;")
        self.url_label.setWordWrap(True)
        self.url_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.url_label)

        layout.addStretch()

        # Large play button
        self.play_btn = QPushButton("▶  Play Station")
        self.play_btn.setFixedHeight(50)
        self.play_btn.setFixedWidth(200)
        self.play_btn.setStyleSheet("font-size: 16px;")
        self.play_btn.clicked.connect(self._on_play)
        layout.addWidget(self.play_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; color: gray;")
        layout.addWidget(self.status_label)

    def set_station(self, name: str, url: str):
        """Update the page with station info."""
        self._current_name = name
        self._current_url = url
        self.name_label.setText(name)
        self.url_label.setText(f"Stream: {url}")
        self.status_label.setText("")

    def _on_play(self):
        if hasattr(self, "_current_url"):
            self.play_requested.emit(self._current_url, self._current_name)
            self.status_label.setText("▶ Now Playing")
