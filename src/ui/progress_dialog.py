"""
Progress Dialog shown during system scan.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


class ScanProgressDialog(QDialog):
    """Progress dialog shown during system scan."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SystemScope — Scanning')
        self.setModal(True)
        layout = QVBoxLayout()
        self.label = QLabel('Collecting system data...')
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.resize(300, 100)