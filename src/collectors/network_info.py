"""
Network Information Collector.
Gathers network interfaces, IP/DNS config, latency, packet loss, and connection status.
Uses psutil, socket (TCP), and PowerShell — avoids ICMP (blocked by most firewalls).
"""

import psutil
import socket
import subprocess
from src.utils import run_silent
import platform
import re
import time
from typing import Any


def tcp_ping(host: str, port: int = 53, timeout: float = 1.0) -> dict:
    """
    Measure latency via TCP connection (bypasses ICMP firewall blocks).
    Connects to DNS port (53) — always open on DNS servers.
    """
    result = {
        "success": False,
        "latency_ms": None,
        "error": None,
    }

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        start = time.perf_counter()
        sock.connect((host, port))
        elapsed = (time.perf_counter() - start) * 1000  # ms

        sock.close()
        result["success"] = True
        result["latency_ms"] = round(elapsed, 2)
    except socket.timeout:
        result["error"] = "Connection timed out"
    except ConnectionRefusedError:
        result["error"] = "Connection refused"
    except Exception as e:
        result["error"] = str(e)

    return result


def measure_latency(host: str = "8.8.8.8", count: int = 5) -> dict:
    """
    Measure latency using TCP connections first (bypasses firewall),
    falls back to ICMP ping if TCP is blocked.
    """
    result = {
        "host": host,
        "packets_sent": count,
        "packets_received": 0,
        "packet_loss_percent": 0,
        "min_ms": None,
        "max_ms": None,
        "avg_ms": None,
        "jitter_ms": None,
        "raw_output": "",
        "method": "tcp",  # or "icmp" if fallback
    }

    latencies = []
    errors = 0

    # Method 1: TCP connections (port 53 for DNS, 80 for HTTP)
    ports_to_try = [53, 80, 443]

    for port in ports_to_try:
        for i in range(count):
            ping_result = tcp_ping(host, port=port, timeout=1.5)
            if ping_result["success"]:
                latencies.append(ping_result["latency_ms"])
            else:
                errors += 1
            time.sleep(0.05)  # Small delay between pings

        # If we got results from this port, no need to try others
        if latencies:
            break

    # If TCP failed completely, fallback to ICMP ping
    if not latencies:
        result["method"] = "icmp"
        try:
            if platform.system() == "Windows":
                cmd = ["ping", "-n", str(count), "-w", "1500", host]
            else:
                cmd = ["ping", "-c", str(count), "-W", "1", host]

            proc = run_silent(cmd, capture_output=True, text=True, timeout=count * 3)
            output = proc.stdout
            result["raw_output"] = output

            # Parse ping results
            loss_match = re.search(r'(\d+)%\s*(packet)?\s*loss', output, re.IGNORECASE)
            if loss_match:
                result["packet_loss_percent"] = int(loss_match.group(1))

            recv_match = re.search(r'Received\s*=\s*(\d+)', output)
            if recv_match:
                result["packets_received"] = int(recv_match.group(1))

            rtt_match = re.search(r'Minimum\s*=\s*(\d+)ms.*?Maximum\s*=\s*(\d+)ms.*?Average\s*=\s*(\d+)ms', output)
            if rtt_match:
                latencies = [
                    float(rtt_match.group(1)),
                    float(rtt_match.group(3)),  # avg
                    float(rtt_match.group(2)),
                ]
                result["packets_received"] = count - (count * result["packet_loss_percent"] // 100)

        except subprocess.TimeoutExpired:
            result["raw_output"] = "Ping timed out"
        except Exception as e:
            result["raw_output"] = str(e)

    # Calculate stats from TCP latencies
    if latencies:
        result["packets_received"] = len(latencies)
        result["min_ms"] = min(latencies)
        result["max_ms"] = max(latencies)
        result["avg_ms"] = sum(latencies) / len(latencies)
        result["jitter_ms"] = result["max_ms"] - result["min_ms"]
        result["packet_loss_percent"] = round((errors / (len(latencies) + errors)) * 100) if (len(latencies) + errors) > 0 else 100
    else:
        result["packet_loss_percent"] = 100
        if not result["raw_output"]:
            result["raw_output"] = "All TCP connections failed and ICMP unavailable"

    return result


def get_network_interfaces() -> list:
    """Get all network interfaces with their addresses."""
    interfaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for iface_name, addr_list in addrs.items():
        iface_info = {
            "name": iface_name,
            "addresses": [],
            "is_up": stats.get(iface_name, None).isup if stats.get(iface_name) else None,
            "speed_mbps": stats.get(iface_name, None).speed if stats.get(iface_name) else None,
            "mtu": stats.get(iface_name, None).mtu if stats.get(iface_name) else None,
            "duplex": str(stats.get(iface_name, None).duplex) if stats.get(iface_name) else None,
        }

        for addr in addr_list:
            addr_info = {
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
            }
            iface_info["addresses"].append(addr_info)

        interfaces.append(iface_info)

    return interfaces


def get_ip_configuration() -> dict:
    """Get IP configuration including gateway and DNS."""
    config = {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "default_gateway": None,
        "dns_servers": [],
        "public_ip": None,
    }

    # Get default gateway via PowerShell
    try:
        result = run_silent(
            ["powershell", "-NoProfile", "-Command",
             "Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -First 1 -ExpandProperty NextHop"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            config["default_gateway"] = result.stdout.strip()
    except Exception:
        pass

    # Get DNS servers
    try:
        result = run_silent(
            ["powershell", "-NoProfile", "-Command",
             "Get-DnsClientServerAddress | Where-Object {$_.AddressFamily -eq 2} | Select-Object -ExpandProperty ServerAddresses"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            config["dns_servers"] = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
    except Exception:
        pass

    return config


def measure_internet_speed_simple(gw: str = None) -> dict:
    """Simple internet connectivity test using TCP connections (parallel)."""
    result = {
        "is_connected": False,
        "latency_google_dns": None,
        "latency_cloudflare": None,
        "latency_gateway": None,
    }

    # Get gateway if not passed
    if gw is None:
        gw = get_ip_configuration().get("default_gateway")
    
    # Run all pings in parallel using ThreadPoolExecutor
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    targets = {
        "google": ("8.8.8.8", 3),
        "cloudflare": ("1.1.1.1", 3),
    }
    if gw:
        targets["gateway"] = (gw, 3)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for name, (host, count) in targets.items():
            future = executor.submit(measure_latency, host, count)
            futures[future] = name
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                ping_result = future.result()
                if name == "google":
                    result["latency_google_dns"] = ping_result
                    if ping_result.get("packet_loss_percent", 100) < 100:
                        result["is_connected"] = True
                elif name == "cloudflare":
                    result["latency_cloudflare"] = ping_result
                elif name == "gateway":
                    result["latency_gateway"] = ping_result
            except Exception:
                pass
    
    return result


def get_network_io_stats() -> dict:
    """Get network I/O counters."""
    io = psutil.net_io_counters(pernic=True)
    total = psutil.net_io_counters()

    per_nic = {}
    for iface, counters in io.items():
        per_nic[iface] = {
            "bytes_sent_mb": round(counters.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(counters.bytes_recv / (1024**2), 2),
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
            "errors_in": counters.errin,
            "errors_out": counters.errout,
            "dropped_in": counters.dropin,
            "dropped_out": counters.dropout,
        }

    return {
        "total": {
            "bytes_sent_mb": round(total.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(total.bytes_recv / (1024**2), 2),
            "packets_sent": total.packets_sent,
            "packets_recv": total.packets_recv,
        },
        "per_interface": per_nic,
    }


def get_active_connections() -> list:
    """Get active network connections."""
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_ESTABLISHED:
                connections.append({
                    "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid,
                })
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    return connections[:50]  # Limit


def get_wifi_info() -> dict:
    """Get WiFi-specific info if available."""
    wifi_info = {"available": False, "ssid": None, "signal": None, "channel": None}

    try:
        result = run_silent(
            ["powershell", "-NoProfile", "-Command",
             "netsh wlan show interfaces | Select-String -Pattern 'SSID|Signal|Channel|BSSID'"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            output = result.stdout
            ssid_match = re.search(r'SSID\s*:\s*(.+)', output)
            signal_match = re.search(r'Signal\s*:\s*(\d+)%', output)
            channel_match = re.search(r'Channel\s*:\s*(\d+)', output)

            wifi_info["available"] = True
            wifi_info["ssid"] = ssid_match.group(1).strip() if ssid_match else None
            wifi_info["signal_percent"] = int(signal_match.group(1)) if signal_match else None
            wifi_info["channel"] = int(channel_match.group(1)) if channel_match else None
    except Exception:
        pass

    return wifi_info


def collect_all() -> dict:
    """Collect all network information (optimized to avoid duplicate calls)."""
    ip_config = get_ip_configuration()
    return {
        "ip_config": ip_config,
        "interfaces": get_network_interfaces(),
        "internet": measure_internet_speed_simple(gw=ip_config.get("default_gateway")),
        "io_stats": get_network_io_stats(),
        "active_connections": get_active_connections(),
        "wifi": get_wifi_info(),
    }
