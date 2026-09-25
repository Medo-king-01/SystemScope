"""
Main Window for SystemScope - Clean version.
5 tabs: System, Network, Storage, Diagnostics, Trends
"""

import sys
import time
import os
import math
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTreeWidget, QTreeWidgetItem, QProgressBar, QTextEdit
)
from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPainter, QPen, QColor

import ctypes
from ctypes import windll


def setup_app_user_model_id():
    """Set AppUserModelID for taskbar icon."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('SystemScope')
    except Exception:
        pass


class DataCollectorWorker(QThread):
    """Worker thread for collecting system data."""
    data_collected = Signal(dict)
    scan_finished = Signal()

    def run(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from src.collectors.system_info import get_system_info, get_gpu_info
        from src.collectors.network_info import get_network_info
        from src.collectors.storage_info import get_storage_info
        from src.database.db import save_snapshot

        data = {
            'timestamp': datetime.now().isoformat(),
            'system': get_system_info(),
            'network': get_network_info(),
            'storage': get_storage_info(),
            'gpu': get_gpu_info()
        }
        save_snapshot(data)
        self.data_collected.emit(data)
        self.scan_finished.emit()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('SystemScope — Local System Intelligence Dashboard')
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Set window icon
        self._set_icon()

        # UI setup
        self._setup_ui()
        self._setup_timer()

    def _set_icon(self):
        """Set window icon via Win32 API."""
        try:
            icon_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / 'assets' / 'icon' / 'app.ico'
            if icon_path.exists():
                hicon = windll.user32.LoadImageW(None, str(icon_path), 1, 0, 0, 0x00000010 | 0x00000020)
                if hicon:
                    windll.user32.SendMessageW(int(self.winId()), 0x0080, 0, int(hicon))
                    windll.user32.SetClassLongPtrW(int(self.winId()), -12, int(hicon))
                    windll.user32.DestroyIcon(hicon)
        except Exception:
            pass

    def _setup_ui(self):
        """Setup UI layout."""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    def _setup_timer(self):
        """Setup manual scan timer."""
        pass

    def start_scan(self):
        """Start manual system scan."""
        self.worker = DataCollectorWorker()
        self.worker.data_collected.connect(self._update_data)
        self.worker.scan_finished.connect(self._scan_done)
        self.worker.start()

    def _update_data(self, data):
        """Update UI with collected data."""
        pass

    def _scan_done(self):
        """Scan finished."""
        pass