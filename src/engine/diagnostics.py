"""
Rule-based Diagnostics Engine.
Evaluates system data against predefined rules and generates recommendations.
No AI involved - pure logic and thresholds.
"""

from typing import Any
from datetime import datetime


class DiagnosticRule:
    """Represents a single diagnostic rule."""

    def __init__(self, rule_id: str, category: str, severity: str,
                 title: str, check_fn, description_fn, recommendation_fn):
        self.rule_id = rule_id
        self.category = category
        self.severity = severity  # "critical", "warning", "info", "good"
        self.title = title
        self.check_fn = check_fn  # Returns True if issue detected
        self.description_fn = description_fn  # Returns description string
        self.recommendation_fn = recommendation_fn  # Returns recommendation string

    def evaluate(self, system_data: dict, network_data: dict, storage_data: dict) -> dict:
        """Evaluate this rule against the data."""
        try:
            triggered = self.check_fn(system_data, network_data, storage_data)
            if triggered:
                return {
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "category": self.category,
                    "title": self.title,
                    "description": self.description_fn(system_data, network_data, storage_data),
                    "recommendation": self.recommendation_fn(system_data, network_data, storage_data),
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            return {
                "rule_id": self.rule_id,
                "severity": "info",
                "category": "error",
                "title": f"Rule '{self.title}' error",
                "description": str(e),
                "recommendation": None,
                "timestamp": datetime.now().isoformat(),
            }
        return None


# ============================================================
# RULE DEFINITIONS
# ============================================================

def create_rules() -> list:
    """Create all diagnostic rules."""
    rules = []

    # ---------- CPU RULES ----------

    rules.append(DiagnosticRule(
        rule_id="cpu_high_usage",
        category="CPU",
        severity="warning",
        title="High CPU Usage",
        check_fn=lambda s, n, st: s.get("cpu", {}).get("cpu_usage_percent", 0) > 85,
        description_fn=lambda s, n, st: f"CPU usage is at {s['cpu']['cpu_usage_percent']}%. This may cause system slowdown.",
        recommendation_fn=lambda s, n, st: "Check top processes for unusual activity. Consider closing unnecessary applications.",
    ))

    rules.append(DiagnosticRule(
        rule_id="cpu_sustained_high",
        category="CPU",
        severity="warning",
        title="Sustained High CPU (per-core max)",
        check_fn=lambda s, n, st: any(c > 90 for c in s.get("cpu", {}).get("cpu_usage_per_core", [])),
        description_fn=lambda s, n, st: f"One or more CPU cores are under heavy load: {s['cpu']['cpu_usage_per_core']}",
        recommendation_fn=lambda s, n, st: "Single-threaded application may be bottlenecking. Check for processes with high CPU usage.",
    ))

    # ---------- RAM RULES ----------

    rules.append(DiagnosticRule(
        rule_id="ram_high_usage",
        category="RAM",
        severity="critical",
        title="Critical RAM Usage",
        check_fn=lambda s, n, st: s.get("ram", {}).get("usage_percent", 0) > 90,
        description_fn=lambda s, n, st: f"RAM usage is critical at {s['ram']['usage_percent']}%. Available: {s['ram']['free_gb']} GB / {s['ram']['total_gb']} GB.",
        recommendation_fn=lambda s, n, st: "Close memory-heavy applications immediately. Consider upgrading RAM if this happens frequently.",
    ))

    rules.append(DiagnosticRule(
        rule_id="ram_moderate_high",
        category="RAM",
        severity="warning",
        title="High RAM Usage",
        check_fn=lambda s, n, st: s.get("ram", {}).get("usage_percent", 0) > 75,
        description_fn=lambda s, n, st: f"RAM usage is high at {s['ram']['usage_percent']}%. Available: {s['ram']['free_gb']} GB.",
        recommendation_fn=lambda s, n, st: "Check top memory-consuming processes. Consider disabling startup programs you don't need.",
    ))

    rules.append(DiagnosticRule(
        rule_id="swap_high_usage",
        category="RAM",
        severity="warning",
        title="Swap File Heavily Used",
        check_fn=lambda s, n, st: s.get("ram", {}).get("swap_percent", 0) > 50,
        description_fn=lambda s, n, st: f"Swap usage is at {s['ram']['swap_percent']}%. System is running low on physical RAM.",
        recommendation_fn=lambda s, n, st: "Your system is relying heavily on disk-based swap, which is very slow. Close applications or add more RAM.",
    ))

    rules.append(DiagnosticRule(
        rule_id="single_process_high_ram",
        category="RAM",
        severity="warning",
        title="Single Process Using Excessive RAM",
        check_fn=lambda s, n, st: any(p.get("memory_mb", 0) > 2048 for p in s.get("processes", [])),
        description_fn=lambda s, n, st: (
            f"Process '{next((p['name'] for p in s['processes'] if p.get('memory_mb', 0) > 2048), 'Unknown')}' "
            f"is using {next((p['memory_mb'] for p in s['processes'] if p.get('memory_mb', 0) > 2048), 0):.0f} MB of RAM."
        ),
        recommendation_fn=lambda s, n, st: "If this is a browser with many tabs, consider closing unused tabs. If it's unexpected, the application may have a memory leak.",
    ))

    # ---------- STORAGE RULES ----------

    rules.append(DiagnosticRule(
        rule_id="disk_critical",
        category="Storage",
        severity="critical",
        title="Critical Disk Space",
        check_fn=lambda s, n, st: any(p.get("usage_percent", 0) > 95 for p in st.get("partitions", [])),
        description_fn=lambda s, n, st: (
            f"Disk {next((p['mountpoint'] for p in st['partitions'] if p.get('usage_percent', 0) > 95), '')} "
            f"is at {next((p['usage_percent'] for p in st['partitions'] if p.get('usage_percent', 0) > 95), 0)}% capacity."
        ),
        recommendation_fn=lambda s, n, st: "Free up disk space immediately. Use the Storage tab to find large files, duplicates, and old files.",
    ))

    rules.append(DiagnosticRule(
        rule_id="disk_high",
        category="Storage",
        severity="warning",
        title="Disk Space Low",
        check_fn=lambda s, n, st: any(p.get("usage_percent", 0) > 85 for p in st.get("partitions", [])),
        description_fn=lambda s, n, st: (
            f"Disk {next((p['mountpoint'] for p in st['partitions'] if p.get('usage_percent', 0) > 85), '')} "
            f"is at {next((p['usage_percent'] for p in st['partitions'] if p.get('usage_percent', 0) > 85), 0)}% capacity."
        ),
        recommendation_fn=lambda s, n, st: "Consider cleaning up disk space. Check the Storage tab for large files and old data.",
    ))

    rules.append(DiagnosticRule(
        rule_id="duplicates_found",
        category="Storage",
        severity="info",
        title="Duplicate Files Found",
        check_fn=lambda s, n, st: len(st.get("duplicates", [])) > 0,
        description_fn=lambda s, n, st: (
            f"Found {len(st['duplicates'])} duplicate files, "
            f"wasting approximately {sum(d.get('size_mb', 0) for d in st['duplicates']):.0f} MB."
        ),
        recommendation_fn=lambda s, n, st: "Review duplicate files in the Storage tab and remove unnecessary copies.",
    ))

    rules.append(DiagnosticRule(
        rule_id="old_files_found",
        category="Storage",
        severity="info",
        title="Old Files Detected",
        check_fn=lambda s, n, st: len(st.get("old_files", [])) > 0,
        description_fn=lambda s, n, st: (
            f"Found {len(st['old_files'])} files not modified in 180+ days, "
            f"using {sum(f.get('size_mb', 0) for f in st['old_files']):.0f} MB."
        ),
        recommendation_fn=lambda s, n, st: "Review old files in the Storage tab. Consider archiving or deleting them.",
    ))

    # ---------- NETWORK RULES ----------

    rules.append(DiagnosticRule(
        rule_id="high_latency",
        category="Network",
        severity="warning",
        title="High Network Latency",
        check_fn=lambda s, n, st: n.get("internet", {}).get("latency_google_dns", {}).get("avg_ms") is not None and n["internet"]["latency_google_dns"]["avg_ms"] > 100,
        description_fn=lambda s, n, st: (
            f"Average latency to Google DNS is {n['internet']['latency_google_dns']['avg_ms']:.0f}ms. "
            f"This may cause slow internet responsiveness."
        ),
        recommendation_fn=lambda s, n, st: "Close bandwidth-heavy applications (streaming, downloads). Check if other devices are using the network.",
    ))

    rules.append(DiagnosticRule(
        rule_id="packet_loss",
        category="Network",
        severity="critical",
        title="Packet Loss Detected",
        check_fn=lambda s, n, st: n.get("internet", {}).get("latency_google_dns", {}).get("packet_loss_percent", 0) > 5,
        description_fn=lambda s, n, st: (
            f"Packet loss to Google DNS is {n['internet']['latency_google_dns']['packet_loss_percent']}%. "
            f"This indicates an unstable connection."
        ),
        recommendation_fn=lambda s, n, st: "Check your network cable/WiFi connection. Restart your router. Contact your ISP if the issue persists.",
    ))

    rules.append(DiagnosticRule(
        rule_id="dns_issue",
        category="Network",
        severity="warning",
        title="DNS Resolution Issues",
        check_fn=lambda s, n, st: n.get("internet", {}).get("latency_google_dns", {}).get("packet_loss_percent", 0) == 100,
        description_fn=lambda s, n, st: "Cannot reach Google DNS. Internet connection may be down or DNS misconfigured.",
        recommendation_fn=lambda s, n, st: "Check if you're connected to the network. Try switching DNS to 8.8.8.8 or 1.1.1.1.",
    ))

    rules.append(DiagnosticRule(
        rule_id="wifi_weak_signal",
        category="Network",
        severity="warning",
        title="Weak WiFi Signal",
        check_fn=lambda s, n, st: n.get("wifi", {}).get("signal_percent", 100) < 40 and n.get("wifi", {}).get("available", False),
        description_fn=lambda s, n, st: f"WiFi signal strength is at {n['wifi']['signal_percent']}%. This will cause slow speeds.",
        recommendation_fn=lambda s, n, st: "Move closer to the router. Check for interference from other devices. Consider a WiFi extender.",
    ))

    # ---------- STARTUP RULES ----------

    rules.append(DiagnosticRule(
        rule_id="too_many_startup",
        category="Startup",
        severity="warning",
        title="Too Many Startup Programs",
        check_fn=lambda s, n, st: len(s.get("startup_items", [])) > 15,
        description_fn=lambda s, n, st: f"You have {len(s['startup_items'])} programs configured to start with Windows. This slows boot time significantly.",
        recommendation_fn=lambda s, n, st: "Disable unnecessary startup programs. Right-click Task Manager → Startup tab → Disable.",
    ))

    rules.append(DiagnosticRule(
        rule_id="startup_heavy_process",
        category="Startup",
        severity="warning",
        title="Heavy Process at Startup",
        check_fn=lambda s, n, st: (
            any(p.get("memory_mb", 0) > 512 and p.get("name", "").lower() in [s.get("name","").lower() for s in s.get("startup_items", [])]
                for p in s.get("processes", []))
        ),
        description_fn=lambda s, n, st: "A startup program is using significant memory. This is wasteful if you don't use it immediately.",
        recommendation_fn=lambda s, n, st: "Consider delaying startup for this application or removing it from startup entirely.",
    ))

    # ---------- SYSTEM RULES ----------

    rules.append(DiagnosticRule(
        rule_id="long_uptime",
        category="System",
        severity="info",
        title="Long Uptime",
        check_fn=lambda s, n, st: s.get("os", {}).get("boot", {}).get("uptime_days", 0) > 7,
        description_fn=lambda s, n, st: f"System has been running for {s['os']['boot']['uptime_formatted']}. A restart may improve performance.",
        recommendation_fn=lambda s, n, st: "Consider restarting your computer to clear temporary states and free memory leaks.",
    ))

    rules.append(DiagnosticRule(
        rule_id="high_process_count",
        category="System",
        severity="warning",
        title="High Number of Processes",
        check_fn=lambda s, n, st: s.get("services", {}).get("total", 0) > 200,
        description_fn=lambda s, n, st: f"System has {s['services']['total']} services installed. More services = more resource usage.",
        recommendation_fn=lambda s, n, st: "Review installed programs and remove ones you don't use. Each installed program may add background services.",
    ))

    # ---------- GOOD STATUS ----------

    rules.append(DiagnosticRule(
        rule_id="system_healthy",
        category="System",
        severity="good",
        title="System Running Smoothly",
        check_fn=lambda s, n, st: (
            s.get("cpu", {}).get("cpu_usage_percent", 0) < 60 and
            s.get("ram", {}).get("usage_percent", 0) < 70 and
            not any(p.get("usage_percent", 0) > 85 for p in st.get("partitions", []))
        ),
        description_fn=lambda s, n, st: "CPU, RAM, and disk usage are within normal ranges.",
        recommendation_fn=lambda s, n, st: "Your system is running well. Continue regular maintenance.",
    ))

    return rules


class DiagnosticsEngine:
    """Engine that runs all rules and compiles diagnostics."""

    def __init__(self):
        self.rules = create_rules()

    def run_diagnostics(self, system_data: dict, network_data: dict, storage_data: dict) -> list:
        """Run all diagnostic rules and return triggered diagnostics."""
        results = []
        for rule in self.rules:
            result = rule.evaluate(system_data, network_data, storage_data)
            if result:
                results.append(result)
        return results

    def get_summary(self, diagnostics: list) -> dict:
        """Get summary of diagnostics by severity."""
        summary = {"critical": 0, "warning": 0, "info": 0, "good": 0, "error": 0}
        for d in diagnostics:
            severity = d.get("severity", "info")
            summary[severity] = summary.get(severity, 0) + 1
        return summary
