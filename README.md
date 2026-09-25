# 🔍 SystemScope — Local System Intelligence Dashboard

A professional Windows desktop application for comprehensive system monitoring, diagnostics, and reporting.

## Features

| Tab | Features |
|-----|----------|
| ⚡ **System** | CPU/RAM/GPU real-time monitoring, temperatures, processes, startup programs |
| 🌐 **Network** | Latency (TCP), packet loss, interfaces, connections, DNS/gateway |
| 💾 **Storage** | Partitions, largest directories, file types, large files, duplicates |
| 🔍 **Diagnostics** | Rule-based engine + Windows Event Logs with filters |
| 📈 **Trends** | QtCharts time-series from SQLite (1h/6h/24h/7d periods) |

## Export Formats

- **🌐 HTML** — Comprehensive report with professional design (dark theme)
- **📋 JSON** — Raw data for analysis/automation
- **📊 CSV** — Diagnostics for spreadsheet apps

## Quick Start

1. Double-click `SystemScope.exe` (no Python required)
2. Click **🔄 Refresh System** to scan CPU/RAM/GPU
3. Click **🔍 Scan Storage** to analyze disk usage
4. Click **📤 Export Report** for HTML/JSON/CSV export

## Architecture

```
src/
├── collectors/          # Data collection layer
│   ├── system_info.py  # CPU/RAM/GPU (psutil + pynvml)
│   ├── network_info.py # TCP ping, interfaces, connections
│   ├── storage_info.py # PowerShell .NET fast file scan
│   └── windows_logs.py # Get-WinEvent integration
├── engine/
│   └── diagnostics.py  # Rule-based diagnostics
├── database/
│   └── db.py           # SQLite storage + history
├── ui/
│   ├── main_window.py  # PySide6 main window (QThread workers)
│   └── trends_tab.py   # QtCharts trend visualization
└── report_generator.py # Professional HTML report builder
```

## Technical Stack

- **GUI:** PySide6 (Qt 6)
- **Data:** psutil, WMI, pywin32, nvidia-ml-py
- **Database:** SQLite
- **Packaging:** PyInstaller

---

Built by **Medo** — SystemScope v1.0