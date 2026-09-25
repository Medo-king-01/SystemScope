"""Rule-based Diagnostics Engine."""

from typing import Any
from datetime import datetime, timedelta


def run_diagnostics(system_data, network_data, storage_data):
    rules = []
    if system_data.get('cpu_percent', 0) > 80:
        rules.append({'level': 'critical', 'message': 'High CPU usage'})
    elif system_data.get('cpu_percent', 0) > 50:
        rules.append({'level': 'warning', 'message': 'Moderate CPU usage'})
    if system_data.get('ram_percent', 0) > 90:
        rules.append({'level': 'critical', 'message': 'Critical RAM usage'})
    elif system_data.get('ram_percent', 0) > 75:
        rules.append({'level': 'warning', 'message': 'High RAM usage'})
    gpu = system_data.get('gpu', {})
    if gpu.get('utilization', 0) > 90:
        rules.append({'level': 'critical', 'message': 'GPU overutilized'})
    return rules

def get_recommendations(rules):
    return [f"URGENT: {r['message']}" if r['level'] == 'critical' else f"Review: {r['message']}" for r in rules]