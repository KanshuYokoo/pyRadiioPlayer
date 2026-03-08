"""Add Station dialog — small popup with name and URL fields."""

from urllib.parse import urlparse

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class AddStationDialog(QDialog):
    """Dialog for adding a new radio station or podcast."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Station")
        self.setFixedSize(420, 220)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Name field
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. My Favorite Station")
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # URL field
        url_label = QLabel("URL:")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("e.g. https://stream.example.com/radio.mp3")
        layout.addWidget(url_label)
        layout.addWidget(self.url_edit)

        # Type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.radio_btn = QRadioButton("Radio Station")
        self.podcast_btn = QRadioButton("Podcast")
        self.radio_btn.setChecked(True)

        self.type_group = QButtonGroup(self)
        self.type_group.addButton(self.radio_btn, 0)
        self.type_group.addButton(self.podcast_btn, 1)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.radio_btn)
        type_layout.addWidget(self.podcast_btn)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # OK / Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_accept(self):
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        if not name or not url:
            return
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Please enter a valid URL starting with http:// or https://",
            )
            return
        self.accept()

    def get_data(self) -> dict:
        """Return the entered station data."""
        return {
            "name": self.name_edit.text().strip(),
            "url": self.url_edit.text().strip(),
            "station_type": "podcast" if self.podcast_btn.isChecked() else "radio",
        }
