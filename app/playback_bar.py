"""Playback bar — play/pause, stop, volume slider, now-playing label."""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class PlaybackBar(QWidget):
    """Bottom bar with playback controls and volume."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self._is_playing = False

        # Audio backend
        self._audio_output = QAudioOutput()
        self._audio_output.setVolume(0.7)
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._player.errorOccurred.connect(self._on_error)

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        # Play / Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.setToolTip("Play / Pause")
        self.play_btn.clicked.connect(self._toggle_play)
        layout.addWidget(self.play_btn)

        # Stop button
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(40, 40)
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.clicked.connect(self._stop)
        layout.addWidget(self.stop_btn)

        # Now-playing label
        self.now_playing_label = QLabel("No station selected")
        self.now_playing_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.now_playing_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.now_playing_label)

        # Volume icon
        vol_label = QLabel("🔊")
        layout.addWidget(vol_label)

        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(120)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        layout.addWidget(self.volume_slider)

    def play_url(self, url: str, station_name: str = ""):
        """Start playing a stream URL."""
        self._player.setSource(QUrl(url))
        self._player.play()
        if station_name:
            self.now_playing_label.setText(f"▶ {station_name}")

    @Slot()
    def _toggle_play(self):
        state = self._player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self._player.play()

    @Slot()
    def _stop(self):
        self._player.stop()
        self.now_playing_label.setText("Stopped")
        self.play_btn.setText("▶")

    @Slot(int)
    def _on_volume_changed(self, value: int):
        self._audio_output.setVolume(value / 100.0)

    @Slot(QMediaPlayer.PlaybackState)
    def _on_state_changed(self, state: QMediaPlayer.PlaybackState):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    @Slot(QMediaPlayer.Error, str)
    def _on_error(self, error, message):
        self.now_playing_label.setText(f"Error: {message}")

    @property
    def player(self) -> QMediaPlayer:
        return self._player
