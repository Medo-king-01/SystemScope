"""
Storage Information Collector - FAST & CLEAN.
✅ No old_files
✅ largest_dirs from file data (no extra scan)
✅ Proper path names
✅ Fast PowerShell .NET scan
"""

import os
import json
import hashlib
import subprocess
from src.utils import run_silent
from pathlib import Path
from datetime import datetime, timedelta

import psutil


def get_disk_partitions() -> list:
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device, "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": usage.total / (1024 ** 3),
                "used_gb": usage.used / (1024 ** 3),
                "free_gb": usage.free / (1024 ** 3),
                "usage_percent": usage.percent,
            })
        except (PermissionError, OSError):
            pass
    return partitions


def _scan_files(base_path: str, max_files: int = 10000) -> list:
    """Fast PowerShell .NET file scan."""
    ps_cmd = f"""
$ErrorActionPreference = 'SilentlyContinue'
$base = '{base_path}'
$files = [System.Collections.Generic.List[object]]::new()
try {{
    $d = [System.IO.DirectoryInfo]::new($base)
    foreach ($f in $d.EnumerateFiles('*','AllDirectories')) {{
        $files.Add([PSCustomObject]@{{
            Path = $f.FullName
            Size = $f.Length
            Ext = if ($f.Extension) {{ $f.Extension.ToLower() }} else {{ '(no ext)' }}
        }})
        if ($files.Count -ge {max_files}) {{ break }}
    }}
}} catch {{
    Get-ChildItem -Path $base -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First {max_files} | ForEach-Object {{
        $files.Add([PSCustomObject]@{{
            Path = $_.FullName
            Size = $_.Length
            Ext = if ($_.Extension) {{ $_.Extension.ToLower() }} else {{ '(no ext)' }}
        }})
    }}
}}
$files | ConvertTo-Json -Compress
"""
    result = run_silent(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=30)
    if result.returncode == 0 and result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    return []


def _get_largest_dirs_from_files(files: list, top_n: int = 15) -> list:
    """Calculate largest directories from file data (TreeSize-like)."""
    dir_sizes = {}
    
    for f in files:
        path = f.get("Path", "")
        size = f.get("Size", 0)
        # Get parent directory
        parent = os.path.dirname(path)
        if parent not in dir_sizes:
            dir_sizes[parent] = 0
        dir_sizes[parent] += size
    
    # Sort by size
    sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for path, size in sorted_dirs[:top_n]:
        results.append({"path": path, "size_gb": size / (1024 ** 3)})
    
    return results


def analyze_files(files: list) -> dict:
    ext_map = {}
    large_files = []
    size_map = {}
    min_large_bytes = 50 * 1024 * 1024
    
    for f in files:
        size = f.get("Size", 0)
        ext = f.get("Ext", "(no ext)")
        path = f.get("Path", "")
        
        if ext not in ext_map:
            ext_map[ext] = {"total_size": 0, "count": 0, "files": []}
        ext_map[ext]["total_size"] += size
        ext_map[ext]["count"] += 1
        if len(ext_map[ext]["files"]) < 3:
            ext_map[ext]["files"].append(path)
        
        if size >= min_large_bytes:
            large_files.append({"path": path, "size_mb": size / (1024 * 1024), "extension": ext})
        
        if size > 1024:
            if size not in size_map:
                size_map[size] = []
            size_map[size].append(path)
    
    large_files.sort(key=lambda x: x["size_mb"], reverse=True)
    
    duplicates = []
    for size, paths in size_map.items():
        if len(paths) < 2:
            continue
        hash_map = {}
        for filepath in paths:
            try:
                h = hashlib.md5(open(filepath, 'rb').read(8192)).hexdigest()
                if h in hash_map:
                    duplicates.append({"size_kb": size / 1024, "original": hash_map[h], "duplicate": filepath, "size_mb": size / (1024 * 1024)})
                    if len(duplicates) >= 50:
                        break
                else:
                    hash_map[h] = filepath
            except (OSError, PermissionError):
                continue
        if len(duplicates) >= 50:
            break
    
    top_by_size = sorted(ext_map.items(), key=lambda x: x[1]["total_size"], reverse=True)[:25]
    file_types = {
        "total_types": len(ext_map),
        "top_by_size": [
            {"extension": ext, "total_size_gb": info["total_size"] / (1024 ** 3), "count": info["count"], "avg_file_size_kb": (info["total_size"] / info["count"] / 1024) if info["count"] > 0 else 0, "sample_files": info["files"][:3]}
            for ext, info in top_by_size
        ],
    }
    
    return {"file_types": file_types, "large_files": large_files[:20], "duplicates": duplicates[:50]}


def collect_all() -> dict:
    user_home = os.path.expanduser("~")
    
    # Partitions
    partitions = get_disk_partitions()
    
    # Fast file scan
    files = _scan_files(user_home, max_files=10000)
    
    # Analyze files
    analysis = analyze_files(files)
    
    # Largest directories (calculated from file data)
    largest_dirs = _get_largest_dirs_from_files(files, top_n=15)
    
    analysis["partitions"] = partitions
    analysis["largest_dirs"] = largest_dirs
    analysis["total_files_scanned"] = len(files)
    analysis["total_size_gb"] = sum(f.get("Size", 0) for f in files) / (1024 ** 3)
    
    return analysis