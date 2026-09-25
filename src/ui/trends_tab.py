"""
Trends Tab — Historical data charts using QtCharts.
Self-contained module for trend visualization.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtGui import QPainter


class TrendsTab(QWidget):
    """Tab showing historical trends from SQLite database using QtCharts."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        # Controls
        controls_layout = QHBoxLayout()
        self.layout.addLayout(controls_layout)

        controls_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"])
        controls_layout.addWidget(self.period_combo)

        controls_layout.addWidget(QLabel("Metric:"))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["CPU + RAM", "CPU Only", "RAM Only"])
        controls_layout.addWidget(self.metric_combo)

        controls_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Load")
        self.refresh_btn.clicked.connect(self._load_data)
        controls_layout.addWidget(self.refresh_btn)

        # Chart
        self.chart = QChart()
        self.chart.setTitle("System Usage Trends")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.cpu_series = QLineSeries()
        self.cpu_series.setName("CPU %")
        self.chart.addSeries(self.cpu_series)

        self.ram_series = QLineSeries()
        self.ram_series.setName("RAM %")
        self.chart.addSeries(self.ram_series)

        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("HH:mm")
        self.axis_x.setTitleText("Time")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.cpu_series.attachAxis(self.axis_x)
        self.ram_series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Usage %")
        self.axis_y.setRange(0, 100)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.cpu_series.attachAxis(self.axis_y)
        self.ram_series.attachAxis(self.axis_y)

        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        self.layout.addWidget(chart_view, stretch=1)

        # Summary
        self.summary_label = QLabel("Click 'Load Data' to view trends")
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.summary_label)

        # Auto-load
        QTimer.singleShot(500, self._load_data)

    def _load_data(self):
        """Load trend data from database."""
        from datetime import datetime, timedelta
        from PySide6.QtCore import QDateTime
        from ..database.db import Database

        period_text = self.period_combo.currentText()
        if "Hour" in period_text and "6" not in period_text:
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

        db = Database()
        try:
            snapshots = db.get_recent_snapshots(limit=1000)
        except Exception:
            snapshots = []
        finally:
            db.close()

        if not snapshots:
            self.summary_label.setText("No historical data — use the app for a while first.")
            return

        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = [s for s in snapshots if datetime.fromisoformat(s.get('timestamp', '2000-01-01')) > cutoff]

        if not filtered:
            self.summary_label.setText(f"No data in the last {hours} hour(s).")
            return

        self.cpu_series.clear()
        self.ram_series.clear()

        cpu_values = []
        ram_values = []

        for snap in filtered:
            dt = QDateTime.fromString(snap['timestamp'], Qt.ISODate)
            ts = dt.toMSecsSinceEpoch()

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

        parts = [f"Snapshots: {len(filtered)}"]
        if cpu_values:
            parts.append(f"CPU avg {sum(cpu_values)/len(cpu_values):.1f}% max {max(cpu_values):.1f}%")
        if ram_values:
            parts.append(f"RAM avg {sum(ram_values)/len(ram_values):.1f}% max {max(ram_values):.1f}%")

        self.summary_label.setText(" | ".join(parts))