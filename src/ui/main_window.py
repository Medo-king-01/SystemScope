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
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QSplineSeries


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


class MetricCard(QFrame):
    """Premium metric card with hover glow and accent border."""

    def __init__(self, title="", value="", subtitle="", progress=None, accent_color=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.accent_color = accent_color or COLORS['accent']
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
                border-top: 3px solid {self.accent_color};
            }}
            MetricCard:hover {{
                background-color: {COLORS['card_hover']};
                border-color: {COLORS['border_light']};
                border-top: 3px solid {self.accent_color};
                box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            }}
            MetricCardLabel {{ color: {COLORS['text_muted']}; font-size: 9pt; font-weight: 500; }}
            MetricCardValue {{ color: {COLORS['text']}; font-size: 24pt; font-weight: bold; }}
            MetricCardSub {{ color: {COLORS['text_muted']}; font-size: 8pt; }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("MetricCardLabel")
        layout.addWidget(title_label)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricCardValue")
        layout.addWidget(self.value_label)
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setObjectName("MetricCardSub")
            layout.addWidget(sub_label)
        if progress is not None:
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximumHeight(6)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setStyleSheet(
                f"QProgressBar {{ border: none; background-color: {COLORS['border']}; border-radius: 3px; }}"
                f"QProgressBar::chunk {{ border-radius: 3px; background-color: {self.accent_color}; }}"
            )
            self.set_progress(progress)
            layout.addWidget(self.progress_bar)
        else:
            self.progress_bar = None

    def set_value(self, value):
        self.value_label.setText(value)

    def set_progress(self, percent):
        if self.progress_bar:
            clamped = min(100, int(percent))
            self.progress_bar.setValue(clamped)
            if clamped > 90:
                self.progress_bar.setStyleSheet(
                    f"QProgressBar {{ border: none; background-color: {COLORS['border']}; border-radius: 3px; }}"
                    f"QProgressBar::chunk {{ border-radius: 3px; background-color: {COLORS['critical']}; }}"
                )
            elif clamped > 75:
                self.progress_bar.setStyleSheet(
                    f"QProgressBar {{ border: none; background-color: {COLORS['border']}; border-radius: 3px; }}"
                    f"QProgressBar::chunk {{ border-radius: 3px; background-color: {COLORS['warning']}; }}"
                )
            else:
                self.progress_bar.setStyleSheet(
                    f"QProgressBar {{ border: none; background-color: {COLORS['border']}; border-radius: 3px; }}"
                    f"QProgressBar::chunk {{ border-radius: 3px; background-color: {self.accent_color}; }}"
                )


class DataCollectorWorker(QThread):
    data_ready = Signal(dict)
    
    def __init__(self, include_storage=False, parent=None):
        super().__init__(parent)
        self.include_storage = include_storage
    
    def run(self):
        result = {}
        try:
            result["system"] = collect_system()
        except Exception:
            result["system"] = {}
        try:
            result["network"] = collect_network()
        except Exception:
            result["network"] = {}
        if self.include_storage:
            try:
                result["storage"] = collect_storage()
            except Exception:
                result["storage"] = {}
        try:
            result["windows_logs"] = collect_windows_logs()
        except Exception:
            result["windows_logs"] = {}
        self.data_ready.emit(result)


class SystemTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        
        self.metrics_layout = QHBoxLayout()
        self.layout.addLayout(self.metrics_layout)
        
        self.cpu_card = MetricCard("المعالج", "—%", progress=0, accent_color=COLORS["accent"])
        self.ram_card = MetricCard("الذاكرة", "— / — GB", progress=0, accent_color=COLORS["accent_secondary"])
        self.gpu_card = MetricCard("كرت الشاشة", "—", accent_color=COLORS["accent_quaternary"])
        self.gpu_temp_card = MetricCard("حرارة كرت الشاشة", "—", accent_color=COLORS["warning"])
        self.gpu_vram_card = MetricCard("VRAM", "—", accent_color=COLORS["info"])
        self.gpu_util_card = MetricCard("حمل كرت الشاشة", "—", accent_color=COLORS["accent_secondary"])
        self.uptime_card = MetricCard("وقت التشغيل", "—", accent_color=COLORS["info"])
        
        for card in [self.cpu_card, self.ram_card, self.gpu_card, self.gpu_util_card,
                     self.gpu_vram_card, self.gpu_temp_card, self.uptime_card]:
            self.metrics_layout.addWidget(card)
        
        splitter = QSplitter(Qt.Vertical)
        self.layout.addWidget(splitter, stretch=1)
        
        proc_group = QGroupBox("Top Processes")
        proc_layout = QVBoxLayout(proc_group)
        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(6)
        self.processes_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Mem (MB)", "Status", "User"])
        self.processes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        proc_layout.addWidget(self.processes_table)
        splitter.addWidget(proc_group)
        
        startup_group = QGroupBox("Startup Programs")
        startup_layout = QVBoxLayout(startup_group)
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(3)
        self.startup_table.setHorizontalHeaderLabels(["Name", "Command", "Location"])
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        startup_layout.addWidget(self.startup_table)
        splitter.addWidget(startup_group)
        
        splitter.setSizes([400, 250])
    
    def update_data(self, data: dict):
        cpu = data.get("cpu", {})
        ram = data.get("ram", {})
        gpu = data.get("gpu", {})
        os_data = data.get("os", {})
        boot = os_data.get("boot", {})
        
        self.cpu_card.set_value(f"{cpu.get('cpu_usage_percent', 0):.0f}%")
        self.cpu_card.set_progress(cpu.get('cpu_usage_percent', 0))
        self.ram_card.set_value(f"{ram.get('used_gb', 0):.1f} / {ram.get('total_gb', 0):.1f} GB")
        self.ram_card.set_progress(ram.get('usage_percent', 0))
        
        primary_gpu = gpu.get('primary_gpu', {})
        if primary_gpu:
            gpu_name = primary_gpu.get('name', 'N/A')
            if len(gpu_name) > 18:
                gpu_name = gpu_name[:15] + "..."
            self.gpu_card.set_value(gpu_name)
            if primary_gpu.get('data_source') == 'pynvml':
                util = primary_gpu.get('gpu_utilization_percent')
                if util is not None:
                    self.gpu_util_card.set_value(f"{util}%")
                    self.gpu_util_card.set_progress(util)
                vram_used = primary_gpu.get('vram_used_mb')
                vram_total = primary_gpu.get('vram_total_mb')
                if vram_used is not None and vram_total:
                    self.gpu_vram_card.set_value(f"{vram_used:.0f} / {vram_total:.0f} MB")
                    self.gpu_vram_card.set_progress((vram_used / vram_total) * 100)
                temp = primary_gpu.get('temperature_c')
                if temp is not None:
                    self.gpu_temp_card.set_value(f"{temp}°C")
        
        self.uptime_card.set_value(boot.get('uptime_formatted', '—'))
        
        processes = data.get("processes", [])
        self.processes_table.setRowCount(min(len(processes), 30))
        for i, proc in enumerate(processes[:30]):
            self.processes_table.setItem(i, 0, QTableWidgetItem(str(proc.get('pid', ''))))
            self.processes_table.setItem(i, 1, QTableWidgetItem(str(proc.get('name', ''))))
            self.processes_table.setItem(i, 2, QTableWidgetItem(f"{proc.get('cpu_percent', 0):.1f}"))
            self.processes_table.setItem(i, 3, QTableWidgetItem(f"{proc.get('memory_mb', 0):.0f}"))
            self.processes_table.setItem(i, 4, QTableWidgetItem(str(proc.get('status', ''))))
            self.processes_table.setItem(i, 5, QTableWidgetItem(str(proc.get('username', ''))))
        
        startup = data.get("startup_items", [])
        self.startup_table.setRowCount(len(startup))
        for i, item in enumerate(startup):
            self.startup_table.setItem(i, 0, QTableWidgetItem(str(item.get('name', ''))))
            self.startup_table.setItem(i, 1, QTableWidgetItem(str(item.get('command', ''))))
            self.startup_table.setItem(i, 2, QTableWidgetItem(str(item.get('location', ''))))


class NetworkTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        
        self.metrics_layout = QHBoxLayout()
        self.layout.addLayout(self.metrics_layout)
        
        self.latency_card = MetricCard("التأخير", "— ms", accent_color=COLORS["accent_secondary"])
        self.loss_card = MetricCard("فقدان الحزم", "—%", accent_color=COLORS["warning"])
        self.gateway_card = MetricCard("البوابة", "—", accent_color=COLORS["info"])
        self.public_ip_card = MetricCard("IP العام", "—", accent_color=COLORS["accent_tertiary"])
        
        for card in [self.latency_card, self.loss_card, self.gateway_card, self.public_ip_card]:
            self.metrics_layout.addWidget(card)
        
        splitter = QSplitter(Qt.Vertical)
        self.layout.addWidget(splitter, stretch=1)
        
        iface_group = QGroupBox("Network Interfaces")
        iface_layout = QVBoxLayout(iface_group)
        self.interfaces_table = QTableWidget()
        self.interfaces_table.setColumnCount(5)
        self.interfaces_table.setHorizontalHeaderLabels(["Name", "IPv4", "Type", "Status", "Speed"])
        self.interfaces_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        iface_layout.addWidget(self.interfaces_table)
        splitter.addWidget(iface_group)
        
        conn_group = QGroupBox("Active Connections")
        conn_layout = QVBoxLayout(conn_group)
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(4)
        self.connections_table.setHorizontalHeaderLabels(["Local", "Remote", "Status", "PID"])
        self.connections_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        conn_layout.addWidget(self.connections_table)
        splitter.addWidget(conn_group)
        
        splitter.setSizes([300, 250])
    
    def update_data(self, data: dict):
        internet = data.get("internet", {})
        ip_config = data.get("ip_config", {})
        google_dns = internet.get("latency_google_dns", {})
        
        avg_latency = google_dns.get("avg_ms")
        self.latency_card.set_value(f"{avg_latency:.0f} ms" if avg_latency else "Timeout")
        self.loss_card.set_value(f"{google_dns.get('packet_loss_percent', 0)}%")
        self.gateway_card.set_value(ip_config.get("default_gateway", "—"))
        
        interfaces = data.get("interfaces", [])
        self.interfaces_table.setRowCount(len(interfaces))
        for i, iface in enumerate(interfaces):
            self.interfaces_table.setItem(i, 0, QTableWidgetItem(iface.get('name', '')))
            addrs = iface.get('addresses', [])
            ipv4 = [a['address'] for a in addrs if 'IPv4' in str(a.get('family', ''))]
            self.interfaces_table.setItem(i, 1, QTableWidgetItem(', '.join(ipv4)))
            self.interfaces_table.setItem(i, 2, QTableWidgetItem(', '.join(set(str(a.get('family', '')) for a in addrs))))
            self.interfaces_table.setItem(i, 3, QTableWidgetItem("Up" if iface.get('is_up') else "Down"))
            speed = iface.get('speed_mbps', 0)
            self.interfaces_table.setItem(i, 4, QTableWidgetItem(f"{speed} Mbps" if speed else "N/A"))
        
        connections = data.get("active_connections", [])
        self.connections_table.setRowCount(min(len(connections), 50))
        for i, conn in enumerate(connections[:50]):
            self.connections_table.setItem(i, 0, QTableWidgetItem(str(conn.get('local_addr', ''))))
            self.connections_table.setItem(i, 1, QTableWidgetItem(str(conn.get('remote_addr', ''))))
            self.connections_table.setItem(i, 2, QTableWidgetItem(str(conn.get('status', ''))))
            self.connections_table.setItem(i, 3, QTableWidgetItem(str(conn.get('pid', ''))))


class StorageTab(QWidget):
    """Fixed: direct call to start_scan, no signal chain issues."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)
        
        # Top controls
        controls_layout = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 Scan Storage (~3s)")
        self.scan_btn.setMinimumWidth(180)
        self.scan_btn.setStyleSheet(f"background-color: {COLORS['good']}; font-size: 11pt;")
        controls_layout.addWidget(self.scan_btn)
        
        self.scan_status = QLabel("Ready — Click Scan to analyze")
        self.scan_status.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 5px 10px;")
        controls_layout.addWidget(self.scan_status, stretch=1)
        
        self.layout.addLayout(controls_layout)
        
        # Disk usage cards
        self.disks_container = QWidget()
        self.disks_layout = QHBoxLayout(self.disks_container)
        self.disks_layout.setSpacing(10)
        self.layout.addWidget(self.disks_container)
        
        # Sub-tabs
        self.sub_tabs = QTabWidget()
        self.layout.addWidget(self.sub_tabs, stretch=1)
        
        # 1. Largest Directories
        largest_widget = QWidget()
        largest_layout = QVBoxLayout(largest_widget)
        self.largest_table = QTableWidget()
        self.largest_table.setColumnCount(3)
        self.largest_table.setHorizontalHeaderLabels(["Directory Name", "Size (GB)", ""])
        self.largest_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.largest_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        largest_layout.addWidget(self.largest_table)
        self.sub_tabs.addTab(largest_widget, "📁 Largest Directories")
        
        # 2. File Types
        types_widget = QWidget()
        types_layout = QVBoxLayout(types_widget)
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(5)
        self.types_table.setHorizontalHeaderLabels(["Extension", "Size (GB)", "Count", "Avg (KB)", "Samples"])
        self.types_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        types_layout.addWidget(self.types_table)
        self.sub_tabs.addTab(types_widget, "📊 File Types")
        
        # 3. Large Files
        large_widget = QWidget()
        large_layout = QVBoxLayout(large_widget)
        self.large_table = QTableWidget()
        self.large_table.setColumnCount(4)
        self.large_table.setHorizontalHeaderLabels(["File Name", "Size (MB)", "Type", "Modified"])
        self.large_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        large_layout.addWidget(self.large_table)
        self.sub_tabs.addTab(large_widget, "📦 Large Files")
        
        # 4. Duplicates
        dup_widget = QWidget()
        dup_layout = QVBoxLayout(dup_widget)
        self.duplicates_table = QTableWidget()
        self.duplicates_table.setColumnCount(4)
        self.duplicates_table.setHorizontalHeaderLabels(["Size (KB)", "Original", "Duplicate", "MB"])
        self.duplicates_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.duplicates_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        dup_layout.addWidget(self.duplicates_table)
        self.sub_tabs.addTab(dup_widget, "🔁 Duplicates")
    
    def start_scan(self):
        """Called directly by main window."""
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳ Scanning...")
        self.scan_status.setText("Scanning storage...")
        # Call parent main window method
        main_window = self.window()
        if hasattr(main_window, '_do_storage_scan'):
            main_window._do_storage_scan()
    
    def update_data(self, data: dict):
        """Update UI with storage data."""
        # Clear disk cards
        while self.disks_layout.count():
            child = self.disks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        partitions = data.get("partitions", [])
        for part in partitions:
            accent = COLORS['accent_secondary'] if part.get('usage_percent', 0) < 70 else COLORS['warning']
            card = MetricCard(
                f"قرص {part.get('mountpoint', '')}",
                f"{part.get('used_gb', 0):.1f} / {part.get('total_gb', 0):.1f} GB",
                f"{part.get('free_gb', 0):.1f} GB free",
                progress=part.get('usage_percent', 0),
                accent_color=accent
            )
            self.disks_layout.addWidget(card)
        self.disks_layout.addStretch()
        
        # Largest directories
        largest = data.get("largest_dirs", [])
        self.largest_table.setRowCount(len(largest))
        for i, d in enumerate(largest):
            full_path = d.get('path', '')
            dir_name = os.path.basename(full_path) or full_path
            size_gb = d.get('size_gb', 0)
            
            name_item = QTableWidgetItem(dir_name)
            name_item.setToolTip(full_path)
            self.largest_table.setItem(i, 0, name_item)
            self.largest_table.setItem(i, 1, QTableWidgetItem(f"{size_gb:.2f}"))
            
            bar = QProgressBar()
            bar.setMaximumHeight(14)
            bar.setTextVisible(False)
            pct = min(100, max(5, int(size_gb * 5)))
            bar.setValue(pct)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {COLORS['info']}; }}")
            self.largest_table.setCellWidget(i, 2, bar)
        
        # File types
        file_types = data.get("file_types", {}).get("top_by_size", [])
        self.types_table.setRowCount(len(file_types))
        for i, t in enumerate(file_types):
            self.types_table.setItem(i, 0, QTableWidgetItem(t.get('extension', '')))
            self.types_table.setItem(i, 1, QTableWidgetItem(f"{t.get('total_size_gb', 0):.3f}"))
            self.types_table.setItem(i, 2, QTableWidgetItem(str(t.get('count', ''))))
            self.types_table.setItem(i, 3, QTableWidgetItem(f"{t.get('avg_file_size_kb', 0):.1f}"))
            samples = ', '.join([os.path.basename(f) for f in t.get('sample_files', [])[:2]])
            self.types_table.setItem(i, 4, QTableWidgetItem(samples))
        
        # Large files
        large_files = data.get("large_files", [])
        self.large_table.setRowCount(len(large_files))
        for i, f in enumerate(large_files):
            full_path = f.get('path', '')
            file_name = os.path.basename(full_path)
            name_item = QTableWidgetItem(file_name)
            name_item.setToolTip(full_path)
            self.large_table.setItem(i, 0, name_item)
            self.large_table.setItem(i, 1, QTableWidgetItem(f"{f.get('size_mb', 0):.1f}"))
            self.large_table.setItem(i, 2, QTableWidgetItem(f.get('extension', '')))
            self.large_table.setItem(i, 3, QTableWidgetItem(f.get('last_modified', '')))
        
        # Duplicates
        duplicates = data.get("duplicates", [])
        self.duplicates_table.setRowCount(len(duplicates))
        for i, d in enumerate(duplicates):
            orig_name = os.path.basename(d.get('original', ''))
            dup_name = os.path.basename(d.get('duplicate', ''))
            orig_item = QTableWidgetItem(orig_name)
            orig_item.setToolTip(d.get('original', ''))
            dup_item = QTableWidgetItem(dup_name)
            dup_item.setToolTip(d.get('duplicate', ''))
            self.duplicates_table.setItem(i, 0, QTableWidgetItem(f"{d.get('size_kb', 0):.1f}"))
            self.duplicates_table.setItem(i, 1, orig_item)
            self.duplicates_table.setItem(i, 2, dup_item)
            self.duplicates_table.setItem(i, 3, QTableWidgetItem(f"{d.get('size_mb', 0):.1f}"))
        
        # Status
        self.scan_status.setText(
            f"✅ {data.get('total_files_scanned', 0):,} files | "
            f"{len(file_types)} types | {len(large_files)} large | {len(duplicates)} dupes"
        )
        
        # Re-enable scan button
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Scan Storage (~3s)")


class DiagnosticsTab(QWidget):
    """Diagnostics tab: Windows Event Logs with filters."""
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        
        # Summary cards
        summary_widget = QWidget()
        summary_layout = QHBoxLayout(summary_widget)
        summary_layout.setSpacing(15)
        self.critical_card = MetricCard("حرج", "0", accent_color=COLORS["critical"])
        self.error_card = MetricCard("أخطاء", "0", accent_color=COLORS["warning"])
        self.warning_card = MetricCard("تحذيرات", "0", accent_color=COLORS["warning"])
        self.info_card = MetricCard("معلومات", "0", accent_color=COLORS["info"])
        for card in [self.critical_card, self.error_card, self.warning_card, self.info_card]:
            summary_layout.addWidget(card)
        self.layout.addWidget(summary_widget)
        
        # Filter section
        filter_group = QGroupBox("Windows Event Log Filters")
        filter_group.setStyleSheet(f"QGroupBox {{ margin-top: 10px; }}" if False else "")
        filter_main_layout = QVBoxLayout(filter_group)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Log:"))
        self.log_source_combo = QComboBox()
        self.log_source_combo.addItems(["System", "Application", "All Logs"])
        row1.addWidget(self.log_source_combo)
        
        row1.addWidget(QLabel("Level:"))
        self.level_filter_combo = QComboBox()
        self.level_filter_combo.addItems(["All", "Critical", "Error", "Warning", "Information"])
        row1.addWidget(self.level_filter_combo)
        
        row1.addWidget(QLabel("Hours:"))
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(1, 168)
        self.hours_spin.setValue(24)
        self.hours_spin.setSuffix("h")
        row1.addWidget(self.hours_spin)
        
        row1.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh Logs")
        self.refresh_btn.setMinimumWidth(140)
        row1.addWidget(self.refresh_btn)
        
        filter_main_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Provider:"))
        self.provider_filter = QComboBox()
        self.provider_filter.addItems(["All Providers"])
        self.provider_filter.setEditable(True)
        self.provider_filter.setMinimumWidth(200)
        row2.addWidget(self.provider_filter)
        
        row2.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter messages...")
        row2.addWidget(self.search_input)
        
        self.apply_filter_btn = QPushButton("🔍 Apply")
        self.apply_filter_btn.clicked.connect(self._apply_filter)
        row2.addWidget(self.apply_filter_btn)
        
        filter_main_layout.addLayout(row2)
        self.layout.addWidget(filter_group)
        
        # Events table
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels(["Time", "Level", "Event ID", "Log", "Provider", "Message"])
        self.events_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setMinimumHeight(200)
        self.events_table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.events_table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.events_table, stretch=1)
        
        # Diagnostics
        diag_group = QGroupBox("System Diagnostics (Rule-Based)")
        diag_layout = QVBoxLayout(diag_group)
        self.diagnostics_table = QTableWidget()
        self.diagnostics_table.setColumnCount(5)
        self.diagnostics_table.setHorizontalHeaderLabels(["Severity", "Category", "Issue", "Description", "Recommendation"])
        self.diagnostics_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.diagnostics_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.diagnostics_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        diag_layout.addWidget(self.diagnostics_table, stretch=1)
        self.diagnostics_table.setMinimumHeight(150)
        self.diagnostics_table.setAlternatingRowColors(True)
        self.diagnostics_table.verticalHeader().setVisible(False)
        self.layout.addWidget(diag_group, stretch=1)
        
        self.current_events = []
    
    def _apply_filter(self):
        if not self.current_events:
            return
        
        level = self.level_filter_combo.currentText()
        provider_text = self.provider_filter.currentText()
        search_text = self.search_input.text().lower()
        
        filtered = self.current_events.copy()
        
        if level != "All":
            filtered = [e for e in filtered if level.lower() in e.get("level", "")]
        
        if provider_text and provider_text != "All Providers":
            filtered = [e for e in filtered if provider_text.lower() in e.get("provider", "").lower()]
        
        if search_text:
            filtered = [e for e in filtered if search_text in e.get("message", "").lower() or search_text in e.get("provider", "").lower()]
        
        self._populate_events_table(filtered)
    
    def refresh_logs(self):
        """Called directly by main window."""
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Loading...")
        main_window = self.window()
        if hasattr(main_window, '_do_refresh_logs'):
            main_window._do_refresh_logs()
    
    def update_logs(self, logs_data: dict):
        self.current_events = []
        for evt in logs_data.get("system_events", []):
            evt["source_log"] = "System"
            self.current_events.append(evt)
        for evt in logs_data.get("application_events", []):
            evt["source_log"] = "Application"
            self.current_events.append(evt)
        
        self.current_events.sort(key=lambda x: x.get("time", ""), reverse=True)
        
        providers = set(e.get("provider", "") for e in self.current_events if e.get("provider"))
        self.provider_filter.clear()
        self.provider_filter.addItem("All Providers")
        self.provider_filter.addItems(sorted(providers))
        
        self._populate_events_table(self.current_events)
        
        summary = logs_data.get("summary", {})
        sys_sum = summary.get("System", {})
        app_sum = summary.get("Application", {})
        critical = sys_sum.get("critical", 0) + app_sum.get("critical", 0)
        errors = sys_sum.get("error", 0) + app_sum.get("error", 0)
        warnings = sys_sum.get("warning", 0) + app_sum.get("warning", 0)
        info_count = len(self.current_events) - critical - errors - warnings
        
        self.critical_card.set_value(str(critical))
        self.error_card.set_value(str(errors))
        self.warning_card.set_value(str(warnings))
        self.info_card.set_value(str(max(0, info_count)))
        
        for card, color in [(self.critical_card, COLORS['critical']), (self.error_card, COLORS['warning']),
                           (self.warning_card, COLORS['warning']), (self.info_card, COLORS['info'])]:
            card.value_label.setStyleSheet(f"color: {color}; font-size: 26pt; font-weight: bold;")
        
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh Logs")
    
    def _populate_events_table(self, events: list):
        self.events_table.setRowCount(min(len(events), 200))
        level_icons = {"critical": "🔴", "error": "⛔", "warning": "⚠️", "information": "ℹ️"}
        level_colors = {"critical": COLORS["critical"], "error": COLORS["warning"], "warning": COLORS["warning"], "information": COLORS["info"]}
        
        for i, evt in enumerate(events[:200]):
            level = evt.get("level", "").lower()
            icon = level_icons.get(level, "⚪")
            
            time_str = evt.get("time", "")[:19]
            self.events_table.setItem(i, 0, QTableWidgetItem(time_str))
            
            level_item = QTableWidgetItem(f"{icon} {level.upper()[:4]}")
            level_item.setForeground(QColor(level_colors.get(level, COLORS["text"])))
            self.events_table.setItem(i, 1, level_item)
            
            self.events_table.setItem(i, 2, QTableWidgetItem(str(evt.get("id", ""))))
            self.events_table.setItem(i, 3, QTableWidgetItem(evt.get("source_log", "")[:12]))
            self.events_table.setItem(i, 4, QTableWidgetItem(evt.get("provider", "")[:30]))
            self.events_table.setItem(i, 5, QTableWidgetItem(evt.get("message", "")[:120]))
    
    def update_diagnostics(self, diagnostics: list, summary: dict):
        self.diagnostics_table.setRowCount(len(diagnostics))
        severity_icons = {"critical": "🔴", "warning": "🟡", "info": "🔵", "good": "🟢"}
        for i, d in enumerate(diagnostics):
            severity = d.get('severity', 'info')
            icon = severity_icons.get(severity, '')
            sev_item = QTableWidgetItem(f"{icon} {severity.upper()}")
            sev_item.setForeground(QColor(COLORS.get(severity, COLORS["text"])))
            self.diagnostics_table.setItem(i, 0, sev_item)
            self.diagnostics_table.setItem(i, 1, QTableWidgetItem(d.get('category', '')))
            self.diagnostics_table.setItem(i, 2, QTableWidgetItem(d.get('title', '')))
            self.diagnostics_table.setItem(i, 3, QTableWidgetItem(d.get('description', '')))
            self.diagnostics_table.setItem(i, 4, QTableWidgetItem(d.get('recommendation', '')))


class TrendsTab(QWidget):
    """Trends tab: Auto-loads data from SQLite."""
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["آخر ساعة", "آخر 6 ساعات", "آخر 24 ساعة", "آخر 7 أيام"])
        self.period_combo.setCurrentIndex(2)
        controls_layout.addWidget(self.period_combo)
        
        controls_layout.addWidget(QLabel("Metric:"))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["المعالج + الذاكرة", "المعالج فقط", "الذاكرة فقط"])
        controls_layout.addWidget(self.metric_combo)
        
        controls_layout.addStretch()
        self.refresh_btn = QPushButton("🔄 تحميل البيانات")
        self.refresh_btn.clicked.connect(self._load_data)
        controls_layout.addWidget(self.refresh_btn)
        
        self.layout.addLayout(controls_layout)

        # Chart
        self.chart = QChart()
        self.chart.setTitle("System Usage Trends")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setBackgroundBrush(QColor(COLORS["card"]))
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        # CPU series
        self.cpu_series = QSplineSeries()
        self.cpu_series.setName("CPU %")
        self.cpu_series.setColor(QColor(COLORS["accent"]))
        pen = self.cpu_series.pen()
        pen.setWidth(2)
        self.cpu_series.setPen(pen)
        self.chart.addSeries(self.cpu_series)

        # RAM series
        self.ram_series = QSplineSeries()
        self.ram_series.setName("RAM %")
        self.ram_series.setColor(QColor(COLORS["accent_secondary"]))
        pen = self.ram_series.pen()
        pen.setWidth(2)
        self.ram_series.setPen(pen)
        self.chart.addSeries(self.ram_series)

        # Axes
        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("HH:mm")
        self.axis_x.setTitleText("Time")
        self.axis_x.setTickCount(8)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.cpu_series.attachAxis(self.axis_x)
        self.ram_series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Usage %")
        self.axis_y.setRange(0, 100)
        self.axis_y.setTickCount(11)
        self.axis_y.setLabelFormat("%d%%")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.cpu_series.attachAxis(self.axis_y)
        self.ram_series.attachAxis(self.axis_y)

        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        self.layout.addWidget(chart_view, stretch=1)

        # Summary
        self.summary_label = QLabel("جاري تحميل البيانات...")
        self.summary_label.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 10px; font-size: 11pt;")
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.summary_label)

        # Auto-load
        QTimer.singleShot(500, self._load_data)
    
    def _load_data(self):
        from PySide6.QtCore import QDateTime, Qt as QtCore

        period_text = self.period_combo.currentText()
        if "1 Hour" in period_text:
            hours = 1
        elif "6 Hours" in period_text:
            hours = 6
        elif "24 Hours" in period_text:
            hours = 24
        elif "7 Days" in period_text:
            hours = 24 * 7
        else:
            hours = 24

        metric = self.metric_combo.currentText()

        try:
            db = Database()
            snapshots = db.get_recent_snapshots(limit=1000)
            db.close()
        except Exception as e:
            self.summary_label.setText(f"خطأ في قاعدة البيانات: {e}")
            return

        if not snapshots:
            self.summary_label.setText("📊 لا توجد بيانات — استخدم التطبيق فترة لجمع البيانات")
            return

        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = [s for s in snapshots if datetime.fromisoformat(s.get('timestamp', '2000-01-01')) > cutoff]

        if not filtered:
            self.summary_label.setText(f"📊 لا توجد بيانات في آخر {hours} ساعة")
            return

        self.cpu_series.clear()
        self.ram_series.clear()

        cpu_values = []
        ram_values = []

        for snap in filtered:
            ts_str = snap.get('timestamp', '')
            try:
                dt = QDateTime.fromString(ts_str, QtCore.ISODate)
                if not dt.isValid():
                    dt = QDateTime.fromString(ts_str, QtCore.ISODateWithMs)
                if not dt.isValid():
                    dt = datetime.fromisoformat(ts_str)
                    dt = QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                ts = dt.toMSecsSinceEpoch()
            except Exception:
                continue

            if metric in ("CPU + RAM", "CPU Only"):
                cpu = snap.get('cpu_usage')
                if cpu is not None:
                    self.cpu_series.append(ts, cpu)
                    cpu_values.append(cpu)

            if metric in ("CPU + RAM", "RAM Only"):
                ram = snap.get('ram_usage')
                if ram is not None:
                    self.ram_series.append(ts, ram)
                    ram_values.append(ram)

        self.cpu_series.setVisible(metric in ("CPU + RAM", "CPU Only"))
        self.ram_series.setVisible(metric in ("CPU + RAM", "RAM Only"))

        if hours > 24:
            self.axis_x.setFormat("dd/MM HH:mm")
        else:
            self.axis_x.setFormat("HH:mm")

        parts = [f"📊 {len(filtered)} عينة"]
        if cpu_values:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            parts.append(f"المعالج: متوسط {avg_cpu:.1f}% | أعلى {max(cpu_values):.1f}%")
        if ram_values:
            avg_ram = sum(ram_values) / len(ram_values)
            parts.append(f"الذاكرة: متوسط {avg_ram:.1f}% | أعلى {max(ram_values):.1f}%")

        self.summary_label.setText("  •  ".join(parts))


class MainWindow(QMainWindow):
    """Main window with direct method calls (no signal chain issues)."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.engine = DiagnosticsEngine()
        self.system_data = {}
        self.network_data = {}
        self.storage_data = {}
        self.windows_logs = {}
        self.diagnostics = []
        self.worker = None
        
        self.last_db_save_time = 0
        self.db_save_interval_seconds = 300
        
        # Setup menu bar with Help > About
        self._setup_menu_bar()
        
        self.setWindowTitle("SystemScope — Local System Intelligence Dashboard")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set window icon via Win32 API
        try:
            import ctypes
            from ctypes.wintypes import HWND
            hwnd = int(self.winId())
            hicon = ctypes.windll.user32.LoadImageW(
                None, 1, 1, 0, 0, 0x00000010 | 0x00000002
            )
            if hicon:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)
                ctypes.windll.user32.SetClassLongPtrW(hwnd, -14, hicon)
                ctypes.windll.user32.SetClassLongPtrW(hwnd, -16, hicon)
        except Exception:
            pass
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Apply premium stylesheet
        self.setStyleSheet(get_stylesheet())
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet(f"QToolBar {{ background-color: {COLORS['card']}; border-bottom: 1px solid {COLORS['border']}; padding: 5px 10px; }}")
        self.addToolBar(toolbar)
        
        self.refresh_btn = QPushButton("🔄 Refresh System")
        self.refresh_btn.setMinimumWidth(150)
        toolbar.addWidget(self.refresh_btn)
        
        toolbar.addWidget(QLabel("Auto:"))
        self.auto_combo = QComboBox()
        self.auto_combo.addItems(["Off", "5s", "10s", "30s", "60s"])
        toolbar.addWidget(self.auto_combo)
        
        toolbar.addSeparator()
        
        self.export_btn = QPushButton("📤 Export Report")
        self.export_btn.setToolTip("Export comprehensive report (HTML / JSON / CSV)")
        toolbar.addWidget(self.export_btn)
        
        toolbar.addSeparator()
        
        self.status_label = QLabel("Ready — Press Refresh to scan")
        toolbar.addWidget(self.status_label)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        main_layout.addWidget(self.tabs)
        
        self.system_tab = SystemTab()
        self.network_tab = NetworkTab()
        self.storage_tab = StorageTab(self)  # Pass parent
        self.diagnostics_tab = DiagnosticsTab()
        self.trends_tab = TrendsTab()
        
        self.tabs.addTab(self.system_tab, "⚡ System")
        self.tabs.addTab(self.network_tab, "🌐 Network")
        self.tabs.addTab(self.storage_tab, "💾 Storage")
        self.tabs.addTab(self.diagnostics_tab, "🔍 Diagnostics")
        self.tabs.addTab(self.trends_tab, "📈 Trends")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("SystemScope v1.0 • Press 🔄 Refresh to scan")
        
        # Connections (direct method calls, no signal chain)
        self.refresh_btn.clicked.connect(self._do_refresh)
        self.auto_combo.currentTextChanged.connect(self._on_auto_changed)
        self.export_btn.clicked.connect(self._export_report)
        self.storage_tab.scan_btn.clicked.connect(self._do_storage_scan)
        self.diagnostics_tab.refresh_btn.clicked.connect(self._do_refresh_logs)
        
        # Timers
        self.fast_timer = QTimer(self)
        self.fast_timer.timeout.connect(self._on_fast_timer)
        self.medium_timer = QTimer(self)
        self.medium_timer.timeout.connect(self._on_medium_timer)
        self.db_cleanup_timer = QTimer(self)
        self.db_cleanup_timer.timeout.connect(self._cleanup_db)
        self.db_cleanup_timer.start(86400000)

    def _on_auto_changed(self, text):
        self.fast_timer.stop()
        self.medium_timer.stop()
        if text == "Off":
            return
        interval = int(text.replace("s", ""))
        self.fast_timer.start(max(1000, interval * 500))
        self.medium_timer.start(interval * 1000)

    def _on_fast_timer(self):
        if self.system_data:
            self.system_tab.update_data(self.system_data)

    def _on_medium_timer(self):
        if self.network_data:
            self.network_tab.update_data(self.network_data)

    def _do_refresh(self):
        """Handle Refresh System button."""
        if self.worker and self.worker.isRunning():
            return
        self.status_label.setText("Scanning...")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Scanning...")
        self.worker = DataCollectorWorker(include_storage=False)
        self.worker.data_ready.connect(self._on_data_ready)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _do_storage_scan(self):
        """Handle Scan Storage button - DIRECT CALL."""
        if self.worker and self.worker.isRunning():
            return
        self.storage_tab.scan_btn.setEnabled(False)
        self.storage_tab.scan_btn.setText("⏳ Scanning...")
        self.storage_tab.scan_status.setText("Scanning storage...")
        self.worker = DataCollectorWorker(include_storage=True)
        self.worker.data_ready.connect(self._on_storage_data_ready)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _do_refresh_logs(self):
        """Handle Refresh Logs button."""
        try:
            self.windows_logs = collect_windows_logs()
            self.diagnostics_tab.update_logs(self.windows_logs)
        except Exception:
            pass

    @Slot(dict)
    def _on_data_ready(self, data: dict):
        """Handle system+network data."""
        self.system_data = data.get("system", {})
        self.network_data = data.get("network", {})
        self.windows_logs = data.get("windows_logs", {})
        
        self.diagnostics = self.engine.run_diagnostics(
            self.system_data, self.network_data, self.storage_data
        )
        summary = self.engine.get_summary(self.diagnostics)
        
        self._save_to_db()
        self.system_tab.update_data(self.system_data)
        self.network_tab.update_data(self.network_data)
        self.diagnostics_tab.update_diagnostics(self.diagnostics, summary)
        self.diagnostics_tab.update_logs(self.windows_logs)
        
        now = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"Last scan: {now}")
        self.status_bar.showMessage(f"SystemScope v1.0 • Last scan: {now}")

    @Slot(dict)
    def _on_storage_data_ready(self, data: dict):
        """Handle storage data - DIRECTLY updates storage tab."""
        self.storage_data = data.get("storage", {})
        self.storage_tab.update_data(self.storage_data)
        self.status_label.setText("Storage scan complete")

    def _save_to_db(self):
        now = time.time()
        if now - self.last_db_save_time >= self.db_save_interval_seconds:
            snapshot_data = {
                "system": self.system_data,
                "network": self.network_data,
                "storage": self.storage_data,
            }
            try:
                snapshot_id = self.db.save_snapshot(snapshot_data)
                for diag in self.diagnostics:
                    self.db.save_diagnostic(
                        snapshot_id, diag["severity"], diag["category"],
                        diag["title"], diag.get("description", ""), diag.get("recommendation", "")
                    )
                self.last_db_save_time = now
            except Exception:
                pass

    def _on_worker_finished(self):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh System")
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def _cleanup_db(self):
        try:
            self.db.cleanup_old_snapshots(days=7)
        except Exception:
            pass

    def _export_report(self):
        """Show export dialog with format options."""
        from pathlib import Path
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
        from src.report_generator import generate_report
        import json, csv

        dialog = QDialog(self)
        dialog.setWindowTitle("📤 Export Report")
        dialog.setFixedSize(420, 280)
        dialog.setStyleSheet(f"QDialog {{ background-color: {COLORS['card']}; }}"
                           f"QLabel {{ color: {COLORS['text']}; }}"
                           f"QPushButton {{ background-color: {COLORS['accent']}; color: white; border: none; "
                           f"border-radius: 6px; padding: 10px 20px; font-weight: bold; min-height: 28px; }}"
                           f"QPushButton:hover {{ background-color: #e62e54; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        title = QLabel("اختر نوع التقرير:")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['accent_secondary']};")
        layout.addWidget(title)
        layout.addSpacing(5)

        def do_export(fmt):
            dialog.accept()
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            if fmt == "html":
                path = Path.home() / f"SystemScope_Report_{ts}.html"
                try:
                    diag = self.diagnostics if isinstance(self.diagnostics, list) else []
                    generate_report(self.system_data, self.network_data, self.storage_data,
                                   self.windows_logs, diag, path)
                    QMessageBox.information(self, "تم التصدير ✅", f"تم حفظ التقرير:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "فشل التصدير ❌", str(e))
            elif fmt == "json":
                path = Path.home() / f"SystemScope_Data_{ts}.json"
                try:
                    data = {"generated_at": datetime.now().isoformat(), "system": self.system_data,
                            "network": self.network_data, "storage": self.storage_data,
                            "windows_logs": self.windows_logs,
                            "diagnostics": self.diagnostics if isinstance(self.diagnostics, list) else []}
                    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
                    QMessageBox.information(self, "تم التصدير ✅", f"تم حفظ البيانات:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "فشل التصدير ❌", str(e))
            elif fmt == "csv":
                path = Path.home() / f"SystemScope_Diagnostics_{ts}.csv"
                try:
                    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                        w = csv.writer(f)
                        w.writerow(["Severity", "Category", "Issue", "Description", "Recommendation"])
                        for d in (self.diagnostics if isinstance(self.diagnostics, list) else []):
                            w.writerow([d.get('severity',''), d.get('category',''), d.get('title',''),
                                       d.get('description',''), d.get('recommendation','')])
                    QMessageBox.information(self, "تم التصدير ✅", f"تم حفظ البيانات:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "فشل التصدير ❌", str(e))

        btn_html = QPushButton("🌐 HTML — تقرير شامل بتصميم احترافي")
        btn_html.clicked.connect(lambda: do_export("html"))
        layout.addWidget(btn_html)

        btn_json = QPushButton("📋 JSON — بيانات خام للتحليل")
        btn_json.clicked.connect(lambda: do_export("json"))
        layout.addWidget(btn_json)

        btn_csv = QPushButton("📊 CSV — التشخيص للجداول")
        btn_csv.clicked.connect(lambda: do_export("csv"))
        layout.addWidget(btn_csv)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.exec()

    def _setup_menu_bar(self):
        """Setup menu bar with Help > About."""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet(f"""
            QMenuBar {{ background-color: {COLORS['card']}; color: {COLORS['text']};
                        border-bottom: 1px solid {COLORS['border']}; padding: 2px 10px; }}
            QMenuBar::item {{ color: {COLORS['text_muted']}; padding: 6px 16px; border-radius: 4px; }}
            QMenuBar::item:selected {{ color: {COLORS['accent']}; background-color: {COLORS['card_hover']}; }}
            QMenu {{ background-color: {COLORS['card']}; color: {COLORS['text']};
                     border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px 0; }}
            QMenu::item {{ padding: 8px 24px; margin: 2px 4px; border-radius: 4px; font-size: 10pt; }}
            QMenu::item:selected {{ background-color: {COLORS['accent']}; color: white; }}
            QMenu::separator {{ height: 1px; background-color: {COLORS['border']}; margin: 4px 10px; }}
        """)
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("ℹ️ About", self._show_about)
        help_menu.addAction("📋 System Requirements", self._show_requirements)
        help_menu.addSeparator()
        help_menu.addAction("🚪 Exit", self.close)

    def _show_about(self):
        """Show About dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, "About SystemScope",
            "<h3 style='color:#E63946;'>🔍 SystemScope v1.0</h3>"
            "<p><b>Local System Intelligence Dashboard</b></p>"
            "<p>Professional Windows system monitoring,<br>"
            "diagnostics, and reporting.</p>"
            "<hr>"
            "<p><b>Built by Medo</b><br>"
            "github.com/Medo-king-01</p>"
            "<hr>"
            "<p><small>MIT License</small></p>"
        )

    def _show_requirements(self):
        """Show System Requirements dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "📋 System Requirements",
            "<h3>System Requirements</h3>"
            "<table cellpadding='6' cellspacing='0'>"
            "<tr><td><b>OS:</b></td><td>Windows 10 or later</td></tr>"
            "<tr><td><b>RAM:</b></td><td>4 GB minimum (8 GB recommended)</td></tr>"
            "<tr><td><b>GPU:</b></td><td>DirectX 10+ (NVIDIA/AMD/Intel)</td></tr>"
            "<tr><td><b>Storage:</b></td><td>50 MB free space</td></tr>"
            "<tr><td><b>Python:</b></td><td>3.10+ (if building from source)</td></tr>"
            "</table>"
            "<hr>"
            "<p><b>Features:</b></p>"
            "• CPU/RAM/GPU monitoring<br>"
            "• Network analysis (TCP ping, interfaces)<br>"
            "• Storage analysis (PowerShell .NET)<br>"
            "• Rule-based diagnostics<br>"
            "• Historical trend charts<br>"
            "• HTML/JSON/CSV export"
        )


def main():
    """Application entry point — loads fonts and launches dashboard."""
    app = QApplication(sys.argv)
    
    # Load Cairo fonts
    loaded = load_fonts()
    if loaded:
        font = QFont("Cairo", 10)
        app.setFont(font)
    
    # Set AppUserModelID BEFORE window creation
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.systemscope.dashboard.v1")
    except Exception:
        pass
    
    window = MainWindow()
    window.setStyleSheet(get_stylesheet())
    window.show()
    
    # Force taskbar icon update using Win32 API directly
    def force_icon_update():
        try:
            import ctypes
            from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM
            
            hwnd = int(window.winId())
            
            hicon = ctypes.windll.user32.LoadImageW(
                None, 1, 1, 0, 0, 0x00000010 | 0x00000002
            )
            
            if hicon:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)
                ctypes.windll.user32.SetClassLongPtrW(hwnd, -14, hicon)
                ctypes.windll.user32.SetClassLongPtrW(hwnd, -16, hicon)
                ctypes.windll.user32.DrawMenuBar(hwnd)
        except Exception:
            pass
    
    from PySide6.QtCore import QTimer
    QTimer.singleShot(500, force_icon_update)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()