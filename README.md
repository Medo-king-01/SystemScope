# 🔍 SystemScope — Local System Intelligence Dashboard

A professional Windows desktop application for comprehensive system monitoring, diagnostics, and reporting.

## 📥 Download

### ✅ Pre-built Executable (Recommended)
1. Go to **[Releases](https://github.com/Medo-king-01/SystemScope/releases)**
2. Download the latest `SystemScope.exe`
3. Double-click to run — **no Python or installation required**

### 🔧 Build from Source
```cmd
git clone https://github.com/Medo-king-01/SystemScope.git
cd SystemScope
pip install -r requirements.txt
python main.py
pyinstaller --onedir --windowed --icon assets/icon/app.ico main.py
```

## ✅ Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **RAM** | 4 GB | 8 GB+ |
| **GPU** | DirectX 10 | DirectX 12 |
| **Storage** | 50 MB | 100 MB |

## 🎨 Tabs

| Tab | Features |
|-----|----------|
| ⚡ **System** | CPU/RAM/GPU monitoring, processes, startup |
| 🌐 **Network** | Latency, packet loss, interfaces, connections |
| 💾 **Storage** | Partitions, largest directories, file types |
| 🔍 **Diagnostics** | Rule-based engine + Windows Event Logs |
| 📈 **Trends** | QtCharts time-series (1h/6h/24h/7d) |

## 💾 Export
- **🌐 HTML** — Professional dark theme report
- **📋 JSON** — Raw data
- **📊 CSV** — Spreadsheet compatible

## 🛠️ Stack: PySide6 + psutil + pynvml + WMI + SQLite + PyInstaller