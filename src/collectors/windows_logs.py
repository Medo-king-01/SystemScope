"""
Windows Event Log Collector.
Gathers errors, warnings, and informational events from Windows Event Log.
Uses PowerShell Get-WinEvent for reliable access.
"""

import subprocess
from src.utils import run_silent
import json
import re
from datetime import datetime, timedelta
from typing import Any


def parse_windows_timestamp(ts_str: str) -> str:
    """Parse Windows PowerShell timestamp formats to ISO format.
    
    Handles:
    - /Date(1790272570667)/  (JavaScript UTC ms timestamp)
    - /Date(1790272570667+0300)/  (with timezone offset)
    - 2025-09-24T10:30:00.000Z  (ISO format)
    - 9/24/2025 10:30:00 AM  (US locale)
    """
    if not ts_str:
        return ""
    
    # Try JavaScript-style: /Date(1790272570667+0300)/
    js_match = re.match(r'/Date\((\d+)([+-]\d{4})?\)/', ts_str)
    if js_match:
        ms = int(js_match.group(1))
        try:
            dt = datetime.utcfromtimestamp(ms / 1000.0)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            pass
    
    # Try ISO format: 2025-09-24T10:30:00.000Z
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # Try: 2025-09-24T10:30:00
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        pass
    
    # Try: 9/24/2025 10:30:00 AM (US locale)
    try:
        dt = datetime.strptime(ts_str, "%m/%d/%Y %I:%M:%S %p")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # Fallback: return as-is
    return ts_str


def get_event_logs(log_name: str = "System", hours: int = 24, max_events: int = 100) -> list:
    """Get events from Windows Event Log.
    
    Args:
        log_name: Log name (System, Application, Security, Setup, etc.)
        hours: Number of hours to look back
        max_events: Maximum events to return
    """
    events = []
    
    try:
        # PowerShell command to get events with proper formatting
        ps_cmd = f"""
        $events = Get-WinEvent -LogName '{log_name}' -MaxEvents {max_events} -ErrorAction SilentlyContinue |
            Where-Object {{ $_.TimeCreated -gt (Get-Date).AddHours(-{hours}) }} |
            Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message |
            Sort-Object TimeCreated -Descending
        $events | ConvertTo-Json -Depth 3 -Compress
        """
        
        result = run_silent(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            
            # Handle single event (dict) vs multiple events (list)
            if isinstance(data, dict):
                data = [data]
            
            for evt in data:
                time_raw = evt.get("TimeCreated", "")
                events.append({
                    "time": parse_windows_timestamp(str(time_raw)),
                    "id": evt.get("Id", ""),
                    "level": evt.get("LevelDisplayName", "").lower(),
                    "provider": evt.get("ProviderName", ""),
                    "message": (evt.get("Message", "") or "")[:500],
                })
    except Exception as e:
        events.append({
            "time": "",
            "id": "",
            "level": "error",
            "provider": "SystemScope",
            "message": f"Could not retrieve {log_name} events: {str(e)}",
        })
    
    return events


def get_critical_events(hours: int = 24, max_events: int = 50) -> list:
    """Get critical and error events from all logs."""
    all_events = []
    
    for log_name in ["System", "Application"]:
        events = get_event_logs(log_name, hours, max_events)
        for evt in events:
            if evt["level"] in ("critical", "error"):
                all_events.append(evt)
    
    # Sort by time
    all_events.sort(key=lambda x: x.get("time", ""), reverse=True)
    return all_events[:max_events]


def get_all_logs_summary(hours: int = 24) -> dict:
    """Get summary from all Windows logs."""
    summary = {
        "System": {"critical": 0, "error": 0, "warning": 0, "info": 0, "events": []},
        "Application": {"critical": 0, "error": 0, "warning": 0, "info": 0, "events": []},
    }
    
    for log_name in summary.keys():
        events = get_event_logs(log_name, hours, 50)
        for evt in events:
            level = evt.get("level", "")
            if level in summary[log_name]:
                summary[log_name][level] += 1
        summary[log_name]["events"] = events[:20]
    
    return summary


def collect_all() -> dict:
    """Collect all Windows Event Log information."""
    return {
        "system_events": get_event_logs("System", hours=24, max_events=50),
        "application_events": get_event_logs("Application", hours=24, max_events=50),
        "critical_events": get_critical_events(hours=24, max_events=50),
        "summary": get_all_logs_summary(hours=24),
    }