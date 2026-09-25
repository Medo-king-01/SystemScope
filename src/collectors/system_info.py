"""
System Information Collector.
Gathers CPU, RAM, GPU, processes.
"""

import psutil
import platform
from pathlib import Path


def get_system_info():
    """Get system information."""
    info = {
        'hostname': platform.node(),
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'cpu_count': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'ram_total': psutil.virtual_memory().total,
        'ram_available': psutil.virtual_memory().available,
        'ram_percent': psutil.virtual_memory().percent
    }
    return info


def get_gpu_info():
    """Get GPU information using pynvml."""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = {
            'name': pynvml.nvmlDeviceGetName(handle),
            'memory_total': pynvml.nvmlDeviceGetMemoryInfo(handle).total,
            'memory_used': pynvml.nvmlDeviceGetMemoryInfo(handle).used,
            'temperature': pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU),
            'utilization': pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        }
        pynvml.nvmlShutdown()
        return info
    except Exception:
        return {'error': 'GPU not available'}


def get_processes(top=10):
    """Get top processes by CPU usage."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            if info['cpu_percent'] > 0:
                procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    return procs[:top]