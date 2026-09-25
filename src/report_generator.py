from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

def generate_report(system_data, network_data, storage_data, windows_logs, diagnostics, output_path):
    """Generate comprehensive HTML report."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = f'''<!DOCTYPE html><html><head><meta charset='UTF-8'><title>SystemScope Report</title><style>body{{font-family:Arial,sans-serif;margin:20px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background-color:#333;color:white}}</style></head><body><h1>SystemScope Report</h1><p>Generated: {ts}</p><h2>System Info</h2><p>CPU: {system_data.get('cpu_percent','N/A')}% | RAM: {system_data.get('ram_percent','N/A')}%</p></body></html>'''  # noqa
    Path(output_path).write_text(html, encoding='utf-8')