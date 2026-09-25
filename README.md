# 🔍 SystemScope — Local System Intelligence Dashboard

A professional Windows desktop application for comprehensive system monitoring, diagnostics, and reporting.

## Features

| Tab | Features |
|-------|----------|
| System | CPU, RAM, GPU, Processes, Services, Startup Programs |
| Network | Interfaces, IP/DNS, Latency, Packet Loss, Connections |
| Storage | Disk Usage, Largest Directories, File Types, File Explorer Scan |
| Diagnostics | Rule-Based Analysis, Windows Event Logs, Recommendations |
| Trends | Historical CPU/RAM Charts (SQLite) |

## Quick Start

```cmd
D:\Projects\SystemScope\run.bat
```

## Build

```cmd
pip install -r requirements.txt
pyinstaller --onedir --windowed --icon assets/icon/app.ico main.py
```