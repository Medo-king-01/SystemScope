# 🔍 SystemScope — Local System Intelligence Dashboard

## 📥 Download
### Pre-built Executable
1. Go to **[Releases](https://github.com/Medo-king-01/SystemScope/releases)**
2. Download `SystemScope.exe`
3. Double-click to run — no Python or installation required

### Build from Source
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
| OS | Windows 10 | Windows 11 |
| RAM | 4 GB | 8 GB+ |
| GPU | DirectX 10 | DirectX 12 |
| Storage | 50 MB | 100 MB |

## 🚀 Quick Start
```cmd
D:\Projects\SystemScope\run.bat
```

### Usage
- **🔄 Refresh System** — scan CPU/RAM/GPU
- **🔍 Scan Storage** — analyze disk usage
- **📊 Trends** — historical charts
- **📤 Export Report** — HTML/JSON/CSV
- **🔍 Diagnostics** — rule-based analysis
- **📋 Windows Logs** — system events

## 🎨 Tabs
| Tab | Features |
|-----|----------|
| ⚡ System | CPU/RAM/GPU, processes, startup |
| 🌐 Network | Latency, packet loss, interfaces |
| 💾 Storage | Partitions, largest directories |
| 🔍 Diagnostics | Rule-based engine + Event Logs |
| 📈 Trends | QtCharts time-series |

## 💾 Export
- **🌐 HTML** — Professional dark theme report
- **📋 JSON** — Raw data for analysis
- **📊 CSV** — Spreadsheet compatible

## 🛠️ Stack
PySide6 | psutil | pynvml | WMI | SQLite | PyInstaller