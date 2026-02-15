"""Podcast detail page — shows podcast info and episode list."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QThread, Slot
from PySide6.QtGui import QFont

from app.services.feed_parser import fetch_episodes, fetch_feed_info


class EpisodeFetchWorker(QThread):
    """Background thread to fetch podcast episodes."""

    from PySide6.QtCore import Signal as _Signal

    finished = _Signal(list, dict)

    def __init__(self, feed_url: str, parent=None):
        super().__init__(parent)
        self.feed_url = feed_url

    def run(self):
        info = fetch_feed_info(self.feed_url)
        episodes = fetch_episodes(self.feed_url)
        self.finished.emit(episodes, info)


class PodcastPage(QWidget):
    """Shows podcast metadata and a scrollable list of episodes."""

    play_requested = Signal(str, str)  # audio_url, episode_title

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        # Podcast title
        self.title_label = QLabel("Select a podcast")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 13px; color: gray;")
        layout.addWidget(self.desc_label)

        # Loading indicator
        self.loading_label = QLabel("")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep)

        # Episodes header
        self.episodes_header = QLabel("Episodes")
        self.episodes_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.episodes_header)

        # Scrollable episode list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.episodes_container = QWidget()
        self.episodes_layout = QVBoxLayout(self.episodes_container)
        self.episodes_layout.setContentsMargins(0, 0, 0, 0)
        self.episodes_layout.setSpacing(4)
        self.episodes_layout.addStretch()

        scroll.setWidget(self.episodes_container)
        layout.addWidget(scroll, stretch=1)

    def set_podcast(self, name: str, feed_url: str):
        """Load podcast info and episodes from the feed URL."""
        self.title_label.setText(name)
        self.desc_label.setText("")
        self.loading_label.setText("Loading episodes…")
        self._clear_episodes()

        self._feed_url = feed_url

        # Fetch in background thread
        self._worker = EpisodeFetchWorker(feed_url)
        self._worker.finished.connect(self._on_episodes_loaded)
        self._worker.start()

    @Slot(list, dict)
    def _on_episodes_loaded(self, episodes: list, info: dict):
        self.loading_label.setText("")
        if info.get("title"):
            self.title_label.setText(info["title"])
        if info.get("description"):
            self.desc_label.setText(info["description"])

        if not episodes:
            self.loading_label.setText("No episodes found.")
            return

        self.episodes_header.setText(f"Episodes ({len(episodes)})")

        for ep in episodes:
            self._add_episode_row(ep)

    def _add_episode_row(self, ep: dict):
        """Add a single episode row to the list."""
        row = QFrame()
        row.setFrameShape(QFrame.Shape.StyledPanel)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 6, 8, 6)
        row_layout.setSpacing(12)

        # Episode info
        info_layout = QVBoxLayout()
        title_lbl = QLabel(ep["title"])
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 600;")
        title_lbl.setWordWrap(True)
        info_layout.addWidget(title_lbl)

        meta_parts = []
        if ep.get("published"):
            meta_parts.append(ep["published"][:16])
        if ep.get("duration"):
            meta_parts.append(f"⏱ {ep['duration']}")
        if meta_parts:
            meta_lbl = QLabel(" · ".join(meta_parts))
            meta_lbl.setStyleSheet("font-size: 11px; color: gray;")
            info_layout.addWidget(meta_lbl)

        row_layout.addLayout(info_layout, stretch=1)

        # Play button
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(36, 36)
        play_btn.setToolTip("Play episode")
        audio_url = ep["audio_url"]
        title = ep["title"]
        play_btn.clicked.connect(lambda checked, u=audio_url, t=title: self.play_requested.emit(u, t))
        row_layout.addWidget(play_btn)

        # Insert before the spacer
        count = self.episodes_layout.count()
        self.episodes_layout.insertWidget(count - 1, row)

    def _clear_episodes(self):
        """Remove all episode rows."""
        while self.episodes_layout.count() > 1:
            item = self.episodes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
