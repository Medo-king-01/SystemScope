"""
Windows Event Log Collector.
Gathers errors, warnings, and informational events.
"""

import subprocess
import json


def get_windows_logs(filter_type='Error', count=50):
    """Get Windows Event Logs."""
    ps_cmd = f"Get-WinEvent -LogName System -MaxEvents {count} | Where-Object {{ $_.LevelDisplayName -eq '{filter_type}' }} | Select-Object TimeCreated, Id, Message | ConvertTo-Json"
    result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, creationflags=0x08000000)
    return result.stdout