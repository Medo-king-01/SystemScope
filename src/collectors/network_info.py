"""
Network Information Collector.
Gathers network interfaces, IP/DNS config, latency, packet loss, and connection status.
"""

import subprocess
import socket
import psutil


def get_network_info():
    """Get network information."""
    interfaces = []
    for name, addrs in psutil.net_if_addrs().items():
        iface = {'name': name, 'addresses': []}
        for addr in addrs:
            iface['addresses'].append({'family': str(addr.family), 'address': addr.address})
        interfaces.append(iface)
    return interfaces


def get_tcp_ping(host="8.8.8.8", port=53, timeout=3):
    """TCP ping to test connectivity."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return {'status': 'success', 'host': host, 'port': port}
    except Exception:
        return {'status': 'failed', 'host': host, 'port': port}


def get_connection_status():
    """Get active connections."""
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        connections.append({
            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
            'status': conn.status
        })
    return connections[:50]


def get_dns_info():
    """Get DNS configuration."""
    import subprocess
    result = subprocess.run(['ipconfig', '/displaydns'], capture_output=True, text=True, creationflags=0x08000000)
    return result.stdout[:5000]