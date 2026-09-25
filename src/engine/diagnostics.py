"""
Rule-based Diagnostics Engine.
No AI involved - pure logic and thresholds.
"""

from typing import Any
from datetime import datetime, timedelta


def run_diagnostics(system_data, network_data, storage_data):
    """Run diagnostics and return recommendations."""
    rules = []
    
    # CPU rule
    if system_data.get('cpu_percent', 0) > 80:
        rules.append({'level': 'critical', 'message': 'High CPU usage detected'})
    elif system_data.get('cpu_percent', 0) > 50:
        rules.append({'level': 'warning', 'message': 'Moderate CPU usage'})
    
    # RAM rule
    if system_data.get('ram_percent', 0) > 90:
        rules.append({'level': 'critical', 'message': 'Critical RAM usage'})
    elif system_data.get('ram_percent', 0) > 75:
        rules.append({'level': 'warning', 'message': 'High RAM usage'})
    
    # GPU rule
    gpu = system_data.get('gpu', {})
    if gpu.get('utilization', 0) > 90:
        rules.append({'level': 'critical', 'message': 'GPU overutilized'})
    
    # Network rule
    if network_data.get('latency', 0) > 100:
        rules.append({'level': 'warning', 'message': 'High network latency'})
    
    # Storage rule
    storage = storage_data.get('disks', [])
    for disk in storage:
        if disk.get('percent', 0) > 90:
            rules.append({'level': 'critical', 'message': f'Disk {disk.get("mountpoint")} nearly full'})
    
    return rules


def get_recommendations(rules):
    """Get recommendations based on rules."""
    recommendations = []
    for rule in rules:
        if rule['level'] == 'critical':
            recommendations.append(f"URGENT: {rule['message']}")
        elif rule['level'] == 'warning':
            recommendations.append(f"Review: {rule['message']}")
    return recommendations