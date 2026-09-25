# 🔍 SystemScope — Local System Intelligence Dashboard

A professional Windows desktop application for comprehensive system monitoring, diagnostics, and reporting.

## 📥 Download

### ✅ Pre-built Executable (Recommended)
1. Go to **[Releases](https://github.com/Medo-king-01/SystemScope/releases)**
2. Download the latest `SystemScope.exe`
3. Double-click to run — **no Python or installation required**

### 🔧 Build from Source
```cmd
# Clone the repository
git clone https://github.com/Medo-king-01/SystemScope.git
cd SystemScope

# Install dependencies
pip install -r requirements.txt

# Run directly
python main.py

# Or build your own executable
pip install pyinstaller
pyinstaller --onedir --windowed --icon assets/icon/app.ico main.py
```

## ✅ Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **RAM** | 4 GB | 8 GB+ |
| **GPU** | DirectX 10 | DirectX 12 (NVIDIA/AMD) |
| **Storage** | 50 MB | 100 MB |
| **Python** | 3.10+ | 3.11+ |

## 🚀 Quick Start

```cmd
D:\Projects\SystemScope\run.bat
```

Or just double-click `SystemScope.exe`.

### Usage
1. Click **🔄 Refresh System** to scan CPU/RAM/GPU
2. Click **🔍 Scan Storage** to analyze disk usage
3. Click **📊 Trends** to view historical charts
4. Click **📤 Export Report** for HTML/JSON/CSV export
5. Click **🔍 Diagnostics** for rule-based analysis
6. Click **📋 Windows Logs** for system event logs

## 🎨 Tabs

| Tab | Features |
|-----|----------|
|| ⚡ **System** | CPU/RAM/GPU monitoring, temperatures, processes, startup programs |
|| 🌐 **Network** | Latency (TCP), packet loss, interfaces, connections, DNS/gateway |
|| 💾 **Storage** | Partitions, largest directories, file types, large files |
|| 🔍 **Diagnostics** | Rule-based engine + Windows Event Logs with filters |

## 💾 Export Formats

- **🌐 HTML** — Comprehensive report with professional dark theme design
- **📋 JSON** — Raw data for analysis/automation
- **📊 CSV** — Diagnostics for spreadsheet apps

## 🛠️ Architecture

```
SystemScope/
├── main.py                  # Entry point
├── run.bat                  # Launcher with environment setup
├── requirements.txt         # Python dependencies
├── assets/
│   └── icon/               # App icons (ICO, PNG)
└── src/
    ├── __init__.py
    ├── utils.py             # run_silent() — console suppression
    ├── report_generator.py  # HTML/JSON/CSV export
    ├── database/
    │   ├── __init__.py
    │   └── db.py            # SQLite storage + history
    ├── collectors/
    │   ├── __init__.py
    │   ├── system_info.py   # CPU/RAM/GPU (psutil + pynvml)
    │   ├── network_info.py  # TCP ping, interfaces, connections
    │   ├── storage_info.py  # PowerShell .NET fast file scan
    │   └── windows_logs.py  # Get-WinEvent integration
    ├── engine/
    │   ├── __init__.py
    │   └── diagnostics.py   # Rule-based diagnostics engine
    └── ui/
        ├── __init__.py
        ├── main_window.py   # PySide6 main window (QThread workers)
        ├── trends_tab.py    # QtCharts trend visualization
        └── progress_dialog.py  # Scan progress dialog
```

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| **GUI** | PySide6 (Qt 6) |
| **CPU/RAM** | psutil |
| **GPU** | pynvml (NVIDIA) |
| **Network** | socket, psutil |
| **Storage** | PowerShell .NET |
| **Logs** | Get-WinEvent |
| **Database** | SQLite |
| **Packaging** | PyInstaller |
| **Charts** | QtCharts |

## 📄 License

MIT License — Free to use, modify, and distribute.

---

Built by **Medo** — [github.com/Medo-king-01](https://github.com/Medo-king-01)
