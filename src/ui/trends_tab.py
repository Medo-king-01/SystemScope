"""
Trends Tab — Historical data charts using QtCharts.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime
import sqlite3


def load_data(db_path, column='cpu_percent'):
    """Load data from database."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f'SELECT timestamp, {column} FROM snapshots ORDER BY timestamp LIMIT 50').fetchall()
    conn.close()
    return rows


class TrendsTab(QWidget):
    """Trends tab widget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Trends')
        layout = QVBoxLayout()
        self.chart_view = QChartView()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

    def update_chart(self, data):
        """Update chart with data."""
        series = QLineSeries()
        for i, (ts, val) in enumerate(data):
            dt = datetime.fromisoformat(ts)
            series.append(QDateTime(QDateTime.fromString(ts.split('T')[0], 'yyyy-MM-dd'), dt.time()), val)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle('CPU Usage Over Time')
        self.chart_view.setChart(chart)