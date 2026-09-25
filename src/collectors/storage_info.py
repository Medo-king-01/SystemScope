"""
Storage Information Collector - FAST & CLEAN.
"""

import os
import json
import subprocess
from pathlib import Path

def get_storage_info():
    """Get storage information."""
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            })
        except PermissionError:
            continue
    return disks


def get_largest_dirs(path, limit=15):
    """Get largest directories."""
    dirs = []
    try:
        for entry in os.scandir(path):
            if entry.is_dir():
                size = sum(f.stat().st_size for f in os.scandir(entry.path) if f.is_file())
                dirs.append({'path': entry.path, 'size': size})
    except PermissionError:
        pass
    dirs.sort(key=lambda x: x['size'], reverse=True)
    return dirs[:limit]


def scan_storage_fast():
    """Fast storage scan using PowerShell."""
    ps_cmd = "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free | ConvertTo-Json"
    result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, creationflags=0x08000000)
    return result.stdout