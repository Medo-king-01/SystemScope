"""
System Information Collector.
Gathers CPU, RAM, GPU, processes, startup programs, services, and disk health.
Uses psutil and WMI (Windows Management Instrumentation).
"""

import psutil
import platform
import subprocess
import json
from datetime import datetime, timedelta
from typing import Any

try:
    import wmi
    HAS_WMI = True
except ImportError:
    HAS_WMI = False


def get_size_gb(bytes_val: float) -> float:
    """Convert bytes to GB with 2 decimal precision."""
    return round(bytes_val / (1024 ** 3), 2)


def get_cpu_info() -> dict:
    """Get CPU information including usage and frequency.
    Uses single blocking call for both overall and per-core usage."""
    # Single call gets both overall and per-core in one shot
    per_core = psutil.cpu_percent(interval=1, percpu=True)
    overall = sum(per_core) / len(per_core) if per_core else 0
    
    info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "current_frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else 0,
        "cpu_usage_percent": round(overall, 1),
        "cpu_usage_per_core": per_core,
        "cpu_times": {
            "user": psutil.cpu_times().user,
            "system": psutil.cpu_times().system,
            "idle": psutil.cpu_times().idle,
        },
        "load_average_1min": psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else None,
    }
    return info


def get_ram_info() -> dict:
    """Get RAM usage details."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    info = {
        "total_gb": get_size_gb(mem.total),
        "available_gb": get_size_gb(mem.available),
        "used_gb": get_size_gb(mem.used),
        "free_gb": get_size_gb(mem.free),
        "usage_percent": mem.percent,
        "active_gb": get_size_gb(mem.active) if hasattr(mem, "active") else None,
        "cached_gb": get_size_gb(mem.cached) if hasattr(mem, "cached") else None,
        "swap_total_gb": get_size_gb(swap.total),
        "swap_used_gb": get_size_gb(swap.used),
        "swap_percent": swap.percent,
    }
    return info


def get_gpu_info() -> dict:
    """Get GPU information using pynvml (NVIDIA) or WMI fallback."""
    gpus = []
    
    # Try pynvml first for real NVIDIA GPU data
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            
            # Basic info
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            gpu_info = {
                "name": name,
                "id": i,
            }
            
            # Driver version
            try:
                driver = pynvml.nvmlSystemGetDriverVersion()
                if isinstance(driver, bytes):
                    driver = driver.decode('utf-8')
                gpu_info["driver_version"] = driver
            except Exception:
                pass
            
            # UUID
            try:
                uuid = pynvml.nvmlDeviceGetUUID(handle)
                if isinstance(uuid, bytes):
                    uuid = uuid.decode('utf-8')
                gpu_info["uuid"] = uuid
            except Exception:
                pass
            
            # Utilization
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_info["gpu_utilization_percent"] = util.gpu
                gpu_info["memory_utilization_percent"] = util.memory
            except Exception:
                gpu_info["gpu_utilization_percent"] = None
                gpu_info["memory_utilization_percent"] = None
            
            # Memory
            try:
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info["vram_total_gb"] = round(mem.total / (1024**3), 2)
                gpu_info["vram_used_gb"] = round(mem.used / (1024**3), 2)
                gpu_info["vram_free_gb"] = round(mem.free / (1024**3), 2)
                gpu_info["vram_used_mb"] = round(mem.used / (1024**2), 0)
                gpu_info["vram_total_mb"] = round(mem.total / (1024**2), 0)
                gpu_info["vram_usage_percent"] = round((mem.used / mem.total) * 100, 1) if mem.total > 0 else 0
            except Exception:
                gpu_info["vram_total_gb"] = None
                gpu_info["vram_used_gb"] = None
                gpu_info["vram_free_gb"] = None
                gpu_info["vram_usage_percent"] = None
            
            # Temperature
            try:
                temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                gpu_info["temperature_c"] = temp
            except Exception:
                gpu_info["temperature_c"] = None
            
            # Power
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle)
                gpu_info["power_watts"] = round(power / 1000, 1)
            except Exception:
                gpu_info["power_watts"] = None
            
            # Clocks
            try:
                core_clock = pynvml.nvmlDeviceGetClockInfo(handle, 0)
                gpu_info["core_clock_mhz"] = core_clock
            except Exception:
                gpu_info["core_clock_mhz"] = None
            
            # PCI info
            try:
                pci = pynvml.nvmlDeviceGetPciInfo(handle)
                gpu_info["pci_bus_id"] = pci.busId
            except Exception:
                pass
            
            # Source
            gpu_info["data_source"] = "pynvml"
            gpus.append(gpu_info)
        
        pynvml.nvmlShutdown()
        
    except (ImportError, Exception):
        # Fallback to WMI if pynvml not available or failed
        if HAS_WMI:
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    gpu_info = {
                        "name": gpu.Name,
                        "driver_version": gpu.DriverVersion,
                        "status": gpu.Status,
                        "adapter_ram_gb": round(int(gpu.AdapterRAM or 0) / (1024**3), 2) if gpu.AdapterRAM and gpu.AdapterRAM > 0 else None,
                        "video_mode": gpu.VideoModeDescription,
                        "pci_id": gpu.PNPDeviceID,
                        "current_refresh_rate": gpu.CurrentRefreshRate,
                        "max_refresh_rate": gpu.MaxRefreshRate,
                        "data_source": "wmi",
                        "gpu_utilization_percent": None,
                        "memory_utilization_percent": None,
                        "vram_used_gb": None,
                        "vram_free_gb": None,
                        "vram_usage_percent": None,
                        "temperature_c": None,
                        "power_watts": None,
                        "core_clock_mhz": None,
                    }
                    gpus.append(gpu_info)
            except Exception:
                pass

    return {
        "count": len(gpus),
        "gpus": gpus,
        "primary_gpu": gpus[0] if gpus else None,
        "has_real_time_data": any(g.get("data_source") == "pynvml" for g in gpus),
    }


def get_processes_info(top_n: int = 30) -> list:
    """Get top N processes by CPU + RAM usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'username', 'create_time', 'num_threads', 'exe']):
        try:
            pinfo = proc.info
            pinfo['memory_mb'] = round(pinfo['memory_info'].rss / (1024**2), 1) if pinfo.get('memory_info') else 0
            pinfo['memory_percent'] = round(proc.memory_percent(), 2)
            # Remove memory_info object (not serializable)
            pinfo.pop('memory_info', None)
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by combined score: CPU + normalized memory
    processes.sort(key=lambda p: (p.get('cpu_percent', 0) or 0) + (p.get('memory_percent', 0) or 0) * 2, reverse=True)
    return processes[:top_n]


def get_startup_programs() -> list:
    """Get Windows startup programs from registry and startup folder."""
    startup_items = []

    # Registry run keys
    import winreg
    reg_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    ]

    for hive, path in reg_paths:
        try:
            with winreg.OpenKey(hive, path) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup_items.append({
                            "name": name,
                            "command": value,
                            "location": f"{'HKCU' if hive == winreg.HKEY_CURRENT_USER else 'HKLM'}\\{path}",
                            "enabled": True,
                            "type": "registry",
                        })
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

    # Startup folder
    import os
    startup_folders = [
        os.path.join(os.environ.get("USERPROFILE", ""), r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
    ]

    for folder in startup_folders:
        import os
        if os.path.exists(folder):
            for item in os.listdir(folder):
                if item.endswith(('.lnk', '.exe', '.bat', '.cmd')):
                    startup_items.append({
                        "name": item,
                        "command": os.path.join(folder, item),
                        "location": folder,
                        "enabled": True,
                        "type": "folder",
                    })

    return startup_items


def get_services_info() -> list:
    """Get Windows services status summary."""
    services = {"running": 0, "stopped": 0, "paused": 0, "total": 0, "auto_start_not_running": []}
    try:
        for svc in psutil.win_service_iter():
            try:
                s = svc.as_dict()
                services["total"] += 1
                if s["status"] == "running":
                    services["running"] += 1
                elif s["status"] == "stopped":
                    services["stopped"] += 1
                elif s["status"] == "paused":
                    services["paused"] += 1

                # Find auto-start services that are stopped
                if s.get("start_type") == "automatic" and s["status"] != "running":
                    services["auto_start_not_running"].append({
                        "name": s["name"],
                        "display_name": s["display_name"],
                        "status": s["status"],
                    })
            except Exception:
                continue
    except Exception:
        pass

    # Limit the list
    services["auto_start_not_running"] = services["auto_start_not_running"][:20]
    return services


def get_disk_health() -> dict:
    """Get disk health info using WMI SMART data."""
    disks = []
    if HAS_WMI:
        try:
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                disk_info = {
                    "model": disk.Model,
                    "interface_type": disk.InterfaceType,
                    "size_gb": get_size_gb(int(disk.Size or 0)),
                    "status": disk.Status,
                    "media_type": disk.MediaType,
                    "serial_number": disk.SerialNumber,
                    "firmware_revision": disk.FirmwareRevision,
                    "partitions": disk.Partitions,
                }
                disks.append(disk_info)
        except Exception as e:
            disks.append({"error": str(e)})
    return {"count": len(disks), "disks": disks}


def get_system_boot_time() -> dict:
    """Get system uptime and boot time."""
    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot
    return {
        "boot_time": boot.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": str(timedelta(seconds=int(uptime.total_seconds()))),
        "uptime_days": round(uptime.total_seconds() / 86400, 1),
    }


def collect_all() -> dict:
    """Collect all system information."""
    return {
        "timestamp": datetime.now().isoformat(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "node": platform.node(),
            "boot": get_system_boot_time(),
        },
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "gpu": get_gpu_info(),
        "processes": get_processes_info(),
        "startup_items": get_startup_programs(),
        "services": get_services_info(),
        "disk_health": get_disk_health(),
    }
