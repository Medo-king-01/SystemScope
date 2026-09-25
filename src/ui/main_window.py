"""
Main Window for SystemScope - Clean version.
"""

import sys
import time
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSplitter, QFrame, QStatusBar, QToolBar,
    QMessageBox, QComboBox, QSpinBox, QLineEdit, QDialog
)
from PySide6.QtCore import QTimer, Qt, Signal, Slot, QThread, QSize
from PySide6.QtGui import QColor, QPainter, QIcon, QFontDatabase, QFont
from pathlib import Path
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis


def resource_path(relative_path):
    """Get absolute path for bundled resources (works with PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def load_fonts():
    """Register Cairo fonts with Qt."""
    font_db = QFontDatabase()
    base = resource_path("assets/fonts")
    font_files = [
        "Cairo-Regular.ttf", "Cairo-Bold.ttf", "Cairo-SemiBold.ttf",
        "Cairo-Medium.ttf", "Cairo-Light.ttf", "Cairo-ExtraBold.ttf",
    ]
    loaded = []
    for f in font_files:
        path = os.path.join(base, f)
        if os.path.exists(path):
            font_id = font_db.addApplicationFont(path)
            if font_id != -1:
                loaded.append(f)
    return loaded


from ..collectors.system_info import collect_all as collect_system
from ..collectors.network_info import collect_all as collect_network
from ..collectors.storage_info import collect_all as collect_storage
from ..collectors.windows_logs import collect_all as collect_windows_logs
from ..engine.diagnostics import DiagnosticsEngine
from ..database.db import Database


COLORS = {
    "background": "#0a0a0a",
    "card": "#111111",
    "card_hover": "#1a1a1a",
    "border": "#2a2a2a",
    "border_light": "#3a3a3a",
    "text": "#f0f0f0",
    "text_muted": "#777777",
    "accent": "#E63946",
    "accent_glow": "#ff4d5a",
    "accent_secondary": "#2EC4B6",
    "accent_tertiary": "#D4E84C",
    "accent_quaternary": "#2D6A4F",
    "warning": "#F4A261",
    "good": "#2D6A4F",
    "critical": "#E63946",
    "info": "#2EC4B6",
}


def get_stylesheet():
    """Premium dark theme stylesheet with Cairo font and refined aesthetics."""
    return f"""
    QMainWindow {{ background-color: {COLORS['background']}; }}
    QWidget {{ background-color: {COLORS['background']}; color: {COLORS['text']};
               font-family: 'Cairo', 'Segoe UI', sans-serif; font-size: 10pt; }}
    * {{ font-family: 'Cairo', 'Segoe UI', sans-serif; }}
    QTabWidget::pane {{ border: 1px solid {COLORS['border']};
                        background-color: {COLORS['card']}; border-radius: 10px; }}
    QTabBar::tab {{ background-color: transparent; color: {COLORS['text_muted']};
                    padding: 12px 28px; margin: 2px; border: none;
                    font-size: 11pt; font-weight: 500;
                    border-bottom: 3px solid transparent; }}
    QTabBar::tab:hover {{ color: {COLORS['text']}; background-color: {COLORS['card_hover']}; border-radius: 6px 6px 0 0; }}
    QTabBar::tab:selected {{ color: {COLORS['accent']}; border-bottom: 3px solid {COLORS['accent']}; background-color: {COLORS['card']}; }}
    QGroupBox {{ background-color: {COLORS['card']}; border: 1px solid {COLORS['border']};
                border-radius: 10px; margin-top: 18px; padding: 18px; font-weight: bold; }}
    QGroupBox::title {{ color: {COLORS['accent']}; subcontrol-origin: margin; left: 15px;
                        padding: 0 10px; font-weight: bold; font-size: 11pt; }}
    QGroupBox:hover {{ border-color: {COLORS['border_light']}; }}
    QPushButton {{ background-color: {COLORS['accent']}; color: white; border: none;
                   border-radius: 8px; padding: 10px 24px; font-weight: bold;
                   min-height: 32px; font-size: 10pt; }}
    QPushButton:hover {{ background-color: {COLORS['accent_glow']}; box-shadow: 0 0 12px {COLORS['accent']}80; }}
    QPushButton:pressed {{ background-color: #c12836; }}
    QPushButton:disabled {{ background-color: #333; color: #666; }}
    QPushButton#secondaryBtn {{ background-color: {COLORS['accent_secondary']}; }}
    QPushButton#secondaryBtn:hover {{ background-color: #3dd4c4; box-shadow: 0 0 12px {COLORS['accent_secondary']}80; }}
    QTableWidget {{ background-color: {COLORS['card']}; border: 1px solid {COLORS['border']};
                    border-radius: 8px; gridline-color: {COLORS['border']};
                    selection-background-color: #2a4f78; alternate-background-color: #0f0f0f; }}
    QTableWidget::item {{ padding: 8px; border-bottom: 1px solid {COLORS['border']}; }}
    QTableWidget::item:selected {{ background-color: #2a4f78; }}
    QHeaderView::section {{ background-color: #1a1a1a; color: {COLORS['text']}; padding: 10px;
                            border: none; border-bottom: 2px solid {COLORS['accent']}; font-weight: bold; }}
    QScrollBar:vertical {{ background-color: {COLORS['card']}; width: 8px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background-color: {COLORS['border_light']}; border-radius: 4px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background-color: {COLORS['accent']}; }}
    QProgressBar {{ border: 1px solid {COLORS['border']}; border-radius: 6px; text-align: center;
                   background-color: {COLORS['card']}; color: {COLORS['text']}; font-weight: bold; }}
    QProgressBar::chunk {{ border-radius: 5px; }}
    QComboBox {{ background-color: {COLORS['card']}; border: 1px solid {COLORS['border']};
                border-radius: 8px; padding: 8px 18px; min-width: 130px; color: {COLORS['text']}; }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox QAbstractItemView {{ background-color: {COLORS['card']}; color: {COLORS['text']};
                                   selection-background-color: {COLORS['accent']}; border: 1px solid {COLORS['border']}; }}
    QSpinBox {{ background-color: {COLORS['card']}; border: 1px solid {COLORS['border']};
                border-radius: 8px; padding: 6px 10px; color: {COLORS['text']}; }}
    QLineEdit {{ background-color: {COLORS['card']}; border: 1px solid {COLORS['border']};
                 border-radius: 8px; padding: 8px 14px; color: {COLORS['text']}; }}
    QLineEdit:focus {{ border-color: {COLORS['accent']}; }}
    QStatusBar {{ background-color: {COLORS['card']}; color: {COLORS['text_muted']}; border-top: 1px solid {COLORS['border']}; }}
    QToolBar {{ background-color: {COLORS['card']}; border-bottom: 1px solid {COLORS['border']}; padding: 6px 12px; spacing: 6px; }}
    QToolBar::separator {{ width: 1px; background-color: {COLORS['border']}; }}
    QLabel {{ color: {COLORS['text']}; }}
    QDialog {{ background-color: {COLORS['card']}; }}
    QCheckBox {{ color: {COLORS['text']}; spacing: 8px; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; border: 2px solid {COLORS['border']}; background-color: {COLORS['card']}; }}
    QCheckBox::indicator:checked {{ background-color: {COLORS['accent']}; border-color: {COLORS['accent']}; }}
    """