"""
SystemScope Report Generator.
Generates comprehensive, professional HTML reports with all system data.
"""

import os
import json
from datetime import datetime
from pathlib import Path


def generate_report(system_data: dict, network_data: dict, storage_data: dict,
                   windows_logs: dict, diagnostics: dict, output_path: Path) -> Path:
    """Generate a comprehensive HTML report."""
    
    timestamp = datetime.now()
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SystemScope Report — {timestamp.strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        {get_report_css()}
    </style>
</head>
<body>
    <div class="container">
        {generate_header(timestamp)}
        {generate_executive_summary(system_data, network_data, diagnostics)}
        {generate_system_section(system_data)}
        {generate_network_section(network_data)}
        {generate_storage_section(storage_data)}
        {generate_diagnostics_section(diagnostics)}
        {generate_windows_logs_section(windows_logs)}
        {generate_footer(timestamp)}
    </div>
    <script>
        {get_report_js()}
    </script>
</body>
</html>"""
    
    output_path.write_text(html, encoding='utf-8')
    return output_path


def get_report_css() -> str:
    return """
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #1f242c;
        --border: #30363d;
        --text-primary: #c9d1d9;
        --text-secondary: #8b949e;
        --accent: #ff3860;
        --accent-secondary: #00d1b2;
        --good: #238636;
        --warning: #ffaa00;
        --critical: #da3633;
        --info: #58a6ff;
    }
    
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        line-height: 1.6;
        direction: rtl;
    }
    
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    
    /* Header */
    .report-header {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .report-header h1 {
        font-size: 28px;
        font-weight: 700;
        color: var(--accent);
    }
    
    .report-header .meta {
        text-align: left;
        color: var(--text-secondary);
        font-size: 13px;
    }
    
    /* Executive Summary */
    .exec-summary {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
    }
    
    .summary-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .summary-card .icon { font-size: 32px; margin-bottom: 8px; }
    .summary-card .value { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
    .summary-card .label { font-size: 12px; color: var(--text-secondary); }
    
    .summary-card.health-good { border-bottom: 3px solid var(--good); }
    .summary-card.health-warning { border-bottom: 3px solid var(--warning); }
    .summary-card.health-critical { border-bottom: 3px solid var(--critical); }
    
    /* Sections */
    .section {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--accent-secondary);
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--border);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-content { display: grid; gap: 20px; }
    
    /* Cards Grid */
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }
    
    .info-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 15px;
    }
    
    .info-card .card-title {
        font-size: 11px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .info-card .card-value {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .info-card .card-sub {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    
    /* Progress Bars */
    .progress-container {
        background: var(--bg-tertiary);
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
        margin-top: 8px;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 6px;
        transition: width 0.3s ease;
    }
    
    .progress-bar.green { background: var(--good); }
    .progress-bar.yellow { background: var(--warning); }
    .progress-bar.red { background: var(--critical); }
    .progress-bar.blue { background: var(--info); }
    
    /* Tables */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    
    .data-table th {
        background: var(--bg-tertiary);
        padding: 10px 12px;
        text-align: right;
        font-weight: 600;
        border-bottom: 2px solid var(--accent);
        color: var(--text-secondary);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .data-table td {
        padding: 10px 12px;
        border-bottom: 1px solid var(--border);
        vertical-align: middle;
    }
    
    .data-table tr:hover td { background: rgba(255,255,255,0.02); }
    
    .data-table .col-size { text-align: left; font-variant-numeric: tabular-nums; }
    .data-table .col-bar { width: 120px; }
    
    /* Severity Badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .badge.critical { background: rgba(214, 54, 51, 0.2); color: var(--critical); }
    .badge.error { background: rgba(255, 170, 0, 0.2); color: var(--warning); }
    .badge.warning { background: rgba(255, 170, 0, 0.15); color: var(--warning); }
    .badge.info { background: rgba(88, 166, 255, 0.2); color: var(--info); }
    .badge.good { background: rgba(35, 134, 54, 0.2); color: var(--good); }
    
    /* Section Divider */
    .divider {
        height: 1px;
        background: var(--border);
        margin: 20px 0;
    }
    
    /* Grid-2 */
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    
    @media (max-width: 768px) {
        .grid-2 { grid-template-columns: 1fr; }
        .report-header { flex-direction: column; text-align: center; }
        .report-header .meta { text-align: center; margin-top: 15px; }
    }
    
    /* Footer */
    .report-footer {
        text-align: center;
        padding: 20px;
        color: var(--text-secondary);
        font-size: 12px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #4a4a4a; }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .section { animation: fadeIn 0.3s ease forwards; }
    .section:nth-child(1) { animation-delay: 0.05s; }
    .section:nth-child(2) { animation-delay: 0.1s; }
    .section:nth-child(3) { animation-delay: 0.15s; }
    .section:nth-child(4) { animation-delay: 0.2s; }
    """


def get_report_js() -> str:
    return """
    // Auto-calculate relative times
    document.addEventListener('DOMContentLoaded', function() {
        // Animate progress bars
        document.querySelectorAll('.progress-bar').forEach(function(bar) {
            var width = bar.getAttribute('data-width');
            if (width) {
                bar.style.width = width + '%';
            }
        });
        
        // Make table headers sortable
        document.querySelectorAll('.data-table th').forEach(function(th, idx) {
            th.style.cursor = 'pointer';
            th.addEventListener('click', function() {
                var table = th.closest('table');
                sortTable(table, idx);
            });
        });
    });
    
    function sortTable(table, col) {
        var rows = Array.from(table.querySelectorAll('tbody tr'));
        var isNumeric = !isNaN(rows[0]?.children[col]?.textContent);
        
        rows.sort(function(a, b) {
            var aVal = a.children[col].textContent.trim();
            var bVal = b.children[col].textContent.trim();
            if (isNumeric) {
                return parseFloat(aVal) - parseFloat(bVal);
            }
            return aVal.localeCompare(bVal, 'ar');
        });
        
        rows.forEach(function(row) { table.querySelector('tbody').appendChild(row); }) ;
    }
    """


def generate_header(timestamp: datetime) -> str:
    return f"""
    <div class="report-header">
        <div>
            <h1>🔍 SystemScope Report</h1>
            <p style="color: var(--text-secondary); margin-top: 5px;">تقرير شامل عن حالة النظام والأداء</p>
        </div>
        <div class="meta">
            <div>📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div>💻 {os.environ.get('COMPUTERNAME', 'Unknown')}</div>
            <div>👤 {os.environ.get('USERNAME', 'Unknown')}</div>
        </div>
    </div>
    """


def generate_executive_summary(sys, net, diagnostics) -> str:
    cpu = sys.get('cpu', {}).get('cpu_usage_percent', 0)
    ram = sys.get('ram', {}).get('usage_percent', 0)
    
    # Calculate health score
    health_score = 100
    if cpu > 80: health_score -= 20
    elif cpu > 60: health_score -= 10
    if ram > 85: health_score -= 20
    elif ram > 70: health_score -= 10
    
    diag_count = len(diagnostics) if isinstance(diagnostics, list) else 0
    critical = sum(1 for d in diagnostics if isinstance(d, dict) and d.get('severity') == 'critical') if isinstance(diagnostics, list) else 0
    
    if critical > 0:
        health = 'critical'
        health_icon = '🔴'
        health_text = 'يحتاج اهتمام'
    elif health_score >= 80:
        health = 'good'
        health_icon = '🟢'
        health_text = 'ممتاز'
    else:
        health = 'warning'
        health_icon = '🟡'
        health_text = 'جيد'
    
    internet_connected = net.get('internet', {}).get('is_connected', False)
    
    return f"""
    <div class="exec-summary">
        <div class="summary-card health-{health}">
            <div class="icon">{health_icon}</div>
            <div class="value">{health_score}%</div>
            <div class="label">صحة النظام — {health_text}</div>
        </div>
        <div class="summary-card">
            <div class="icon">⚡</div>
            <div class="value">{cpu:.0f}%</div>
            <div class="label">استخدام المعالج</div>
        </div>
        <div class="summary-card">
            <div class="icon">🧠</div>
            <div class="value">{ram:.0f}%</div>
            <div class="label">استخدام الذاكرة</div>
        </div>
        <div class="summary-card">
            <div class="icon">🌐</div>
            <div class="value">{'✅' if internet_connected else '❌'}</div>
            <div class="label">اتصال الإنترنت</div>
        </div>
        <div class="summary-card">
            <div class="icon">🔍</div>
            <div class="value">{diag_count}</div>
            <div class="label">تنبيهات التشخيص</div>
        </div>
    </div>
    """


def generate_system_section(data: dict) -> str:
    if not data:
        return ''
    
    cpu = data.get('cpu', {})
    ram = data.get('ram', {})
    gpu = data.get('gpu', {}).get('primary_gpu', {})
    os_info = data.get('os', {})
    boot = os_info.get('boot', {})
    
    ram_total = ram.get('total_gb', 0)
    ram_used = ram.get('used_gb', 0)
    ram_pct = ram.get('usage_percent', 0)
    
    cpu_pct = cpu.get('cpu_usage_percent', 0)
    
    # Processes table
    processes_html = ""
    for proc in data.get('processes', [])[:15]:
        processes_html += f"""
        <tr>
            <td>{proc.get('pid', '')}</td>
            <td>{proc.get('name', '')}</td>
            <td class="col-size">{proc.get('cpu_percent', 0):.1f}%</td>
            <td class="col-size">{proc.get('memory_mb', 0):.0f} MB</td>
            <td><span class="badge {'error' if proc.get('cpu_percent', 0) > 50 else 'info'}">{proc.get('status', '')}</span></td>
        </tr>
        """
    
    # Startup items
    startup_html = ""
    for item in data.get('startup_items', [])[:10]:
        startup_html += f"""
        <tr>
            <td>{item.get('name', '')}</td>
            <td><code>{item.get('command', '')[:80]}</code></td>
            <td>{item.get('location', '')}</td>
        </tr>
        """
    
    return f"""
    <div class="section">
        <div class="section-title">⚡ System Information</div>
        <div class="section-content">
            <div class="cards-grid">
                <div class="info-card">
                    <div class="card-title">المعالج (CPU)</div>
                    <div class="card-value">{cpu.get('processor', 'N/A')}</div>
                    <div class="card-sub">{cpu.get('physical_cores', 0)} نواة فيزيائية / {cpu.get('logical_cores', 0)} منطقية</div>
                    <div class="progress-container">
                        <div class="progress-bar {'red' if cpu_pct > 75 else 'yellow' if cpu_pct > 50 else 'green'}" data-width="{cpu_pct}"></div>
                    </div>
                </div>
                <div class="info-card">
                    <div class="card-title">الذاكرة (RAM)</div>
                    <div class="card-value">{ram_used:.1f} / {ram_total:.1f} GB</div>
                    <div class="card-sub">متاح: {ram.get('free_gb', 0):.1f} GB</div>
                    <div class="progress-container">
                        <div class="progress-bar {'red' if ram_pct > 85 else 'yellow' if ram_pct > 70 else 'green'}" data-width="{ram_pct}"></div>
                    </div>
                </div>
                <div class="info-card">
                    <div class="card-title">كرت الشاشة (GPU)</div>
                    <div class="card-value">{gpu.get('name', 'N/A')[:30]}</div>
                    <div class="card-sub">
                        {'VRAM: ' + f"{gpu.get('vram_used_mb', 0):.0f}/{gpu.get('vram_total_mb', 0):.0f} MB" if gpu.get('data_source') == 'pynvml' else gpu.get('vram_gb', 'N/A')}
                        {' | حرارة: ' + str(gpu.get('temperature_c', '')) + '°C' if gpu.get('temperature_c') else ''}
                    </div>
                </div>
                <div class="info-card">
                    <div class="card-title">نظام التشغيل</div>
                    <div class="card-value">{os_info.get('name', 'N/A')}</div>
                    <div class="card-sub">{os_info.get('version', '')} | معمارية {os_info.get('architecture', '')}</div>
                    <div class="card-sub">وقت التشغيل: {boot.get('uptime_formatted', 'N/A')}</div>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">🔥 أعلى 15 عملية استهلاكاً</h3>
            <table class="data-table">
                <thead><tr><th>PID</th><th>العملية</th><th>المعالج</th><th>الذاكرة</th><th>الحالة</th></tr></thead>
                <tbody>{processes_html if processes_html else '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary)">لا توجد بيانات</td></tr>'}</tbody>
            </table>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">🚀 برامج بدء التشغيل</h3>
            <table class="data-table">
                <thead><tr><th>الاسم</th><th>المسار</th><th>الموقع</th></tr></thead>
                <tbody>{startup_html if startup_html else '<tr><td colspan="3" style="text-align:center;color:var(--text-secondary)">لا توجد بيانات</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    """


def generate_network_section(data: dict) -> str:
    if not data:
        return ''
    
    internet = data.get('internet', {})
    google = internet.get('latency_google_dns', {})
    ip_config = data.get('ip_config', {})
    
    # Interfaces
    interfaces_html = ""
    for iface in data.get('interfaces', []):
        addrs = iface.get('addresses', [])
        ipv4 = ', '.join([a['address'] for a in addrs if 'IPv4' in str(a.get('family', ''))])
        status_badge = '<span class="badge good">Up</span>' if iface.get('is_up') else '<span class="badge error">Down</span>'
        interfaces_html += f"""
        <tr>
            <td>{iface.get('name', '')}</td>
            <td>{ipv4 or 'N/A'}</td>
            <td>{status_badge}</td>
            <td class="col-size">{iface.get('speed_mbps', 0)} Mbps</td>
        </tr>
        """
    
    # Connections
    connections_html = ""
    for conn in data.get('active_connections', [])[:15]:
        status = conn.get('status', '')
        badge_class = 'good' if status == 'ESTABLISHED' else 'warning' if status == 'TIME_WAIT' else 'info'
        connections_html += f"""
        <tr>
            <td><code>{conn.get('local_addr', '')}</code></td>
            <td><code>{conn.get('remote_addr', '')}</code></td>
            <td><span class="badge {badge_class}">{status}</span></td>
            <td>{conn.get('pid', '')}</td>
        </tr>
        """
    
    return f"""
    <div class="section">
        <div class="section-title">🌐 Network Information</div>
        <div class="section-content">
            <div class="cards-grid">
                <div class="info-card">
                    <div class="card-title">اتصال الإنترنت</div>
                    <div class="card-value">{'✅ متصل' if internet.get('is_connected') else '❌ غير متصل'}</div>
                    <div class="card-sub">البوابة: {ip_config.get('default_gateway', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="card-title">الاستجابة (Latency)</div>
                    <div class="card-value">{google.get('avg_ms', 0):.1f} ms</div>
                    <div class="card-sub">فقدان الحزم: {google.get('packet_loss_percent', 0)}%</div>
                </div>
                <div class="info-card">
                    <div class="card-title">عناوين DNS</div>
                    <div class="card-value" style="font-size: 14px;">{', '.join(ip_config.get('dns_servers', [])[:3])}</div>
                    <div class="card-sub">عامة: {ip_config.get('public_ip', 'N/A')}</div>
                </div>
                <div class="info-card">
                    <div class="card-title">MAC Address</div>
                    <div class="card-value" style="font-size: 14px;">{ip_config.get('mac_address', 'N/A')}</div>
                    <div class="card-sub">DHCP: {'مفعل' if ip_config.get('dhcp_enabled') else 'معطل'}</div>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">🔌 واجهات الشبكة</h3>
            <table class="data-table">
                <thead><tr><th>الواجهة</th><th>عنوان IP</th><th>الحالة</th><th>السرعة</th></tr></thead>
                <tbody>{interfaces_html if interfaces_html else '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">لا توجد بيانات</td></tr>'}</tbody>
            </table>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">🔗 الاتصالات النشطة (أول 15)</h3>
            <table class="data-table">
                <thead><tr><th>المحلي</th><th>البعيد</th><th>الحالة</th><th>PID</th></tr></thead>
                <tbody>{connections_html if connections_html else '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">لا توجد بيانات</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    """


def generate_storage_section(data: dict) -> str:
    if not data:
        return ''
    
    # Partitions
    partitions_html = ""
    total_size = 0
    total_used = 0
    for p in data.get('partitions', []):
        pct = p.get('usage_percent', 0)
        total_size += p.get('total_gb', 0)
        total_used += p.get('used_gb', 0)
        partitions_html += f"""
        <tr>
            <td>{p.get('mountpoint', '')}</td>
            <td class="col-size">{p.get('total_gb', 0):.1f} GB</td>
            <td class="col-size">{p.get('used_gb', 0):.1f} GB</td>
            <td class="col-size">{p.get('free_gb', 0):.1f} GB</td>
            <td class="col-bar">
                <div class="progress-container">
                    <div class="progress-bar {'red' if pct > 85 else 'yellow' if pct > 70 else 'green'}" data-width="{pct}"></div>
                </div>
            </td>
            <td class="col-size">{pct}%</td>
        </tr>
        """
    
    # Largest directories
    largest_html = ""
    max_size = max((d.get('size_gb', 1) for d in data.get('largest_dirs', [])), default=1)
    for d in data.get('largest_dirs', [])[:15]:
        pct = (d.get('size_gb', 0) / max_size) * 100 if max_size > 0 else 0
        largest_html += f"""
        <tr>
            <td>{os.path.basename(d.get('path', ''))}</td>
            <td class="col-size">{d.get('size_gb', 0):.2f} GB</td>
            <td class="col-bar">
                <div class="progress-container">
                    <div class="progress-bar blue" data-width="{pct:.0f}"></div>
                </div>
            </td>
        </tr>
        """
    
    # File types
    types_html = ""
    for t in data.get('file_types', {}).get('top_by_size', [])[:15]:
        samples = ', '.join([os.path.basename(f) for f in t.get('sample_files', [])[:2]])
        types_html += f"""
        <tr>
            <td><code>{t.get('extension', '')}</code></td>
            <td class="col-size">{t.get('total_size_gb', 0):.3f} GB</td>
            <td class="col-size">{t.get('count', 0):,}</td>
            <td class="col-size">{t.get('avg_file_size_kb', 0):.1f} KB</td>
            <td><span style="color: var(--text-secondary); font-size: 11px;">{samples}</span></td>
        </tr>
        """
    
    # Large files
    large_html = ""
    for f in data.get('large_files', [])[:15]:
        large_html += f"""
        <tr>
            <td>{os.path.basename(f.get('path', ''))}</td>
            <td class="col-size">{f.get('size_mb', 0):.1f} MB</td>
            <td><code>{f.get('extension', '')}</code></td>
            <td>{f.get('last_modified', '')}</td>
        </tr>
        """
    
    # Duplicates
    dupes_html = ""
    for d in data.get('duplicates', [])[:20]:
        dupes_html += f"""
        <tr>
            <td class="col-size">{d.get('size_kb', 0):.1f} KB</td>
            <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;">{os.path.basename(d.get('original', ''))}</td>
            <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis;">{os.path.basename(d.get('duplicate', ''))}</td>
            <td class="col-size">{d.get('size_mb', 0):.1f} MB</td>
        </tr>
        """
    
    total_pct = (total_used / total_size * 100) if total_size > 0 else 0
    
    return f"""
    <div class="section">
        <div class="section-title">💾 Storage Analysis</div>
        <div class="section-content">
            <div class="cards-grid">
                <div class="info-card">
                    <div class="card-title">إجمالي المساحة</div>
                    <div class="card-value">{total_size:.1f} GB</div>
                    <div class="card-sub">المستخدم: {total_used:.1f} GB ({total_pct:.1f}%)</div>
                    <div class="progress-container">
                        <div class="progress-bar {'red' if total_pct > 85 else 'yellow' if total_pct > 70 else 'green'}" data-width="{total_pct}"></div>
                    </div>
                </div>
                <div class="info-card">
                    <div class="card-title">الملفات المفحوصة</div>
                    <div class="card-value">{data.get('total_files_scanned', 0):,}</div>
                    <div class="card-sub">الحجم الإجمالي: {data.get('total_size_gb', 0):.2f} GB</div>
                </div>
                <div class="info-card">
                    <div class="card-title">الملفات الكبيرة</div>
                    <div class="card-value">{len(data.get('large_files', []))}</div>
                    <div class="card-sub">أكبر من 50 ميجابايت</div>
                </div>
                <div class="info-card">
                    <div class="card-title">الملفات المكررة</div>
                    <div class="card-value">{len(data.get('duplicates', []))}</div>
                    <div class="card-sub">مجموعة بنفس الحجم والمحتوى</div>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">💿 أقسام القرص</h3>
            <table class="data-table">
                <thead><tr><th>القسم</th><th>الحجم</th><th>المستخدم</th><th>المتاح</th><th></th><th></th></tr></thead>
                <tbody>{partitions_html}</tbody>
            </table>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">📁 أكبر 15 دليل</h3>
            <table class="data-table">
                <thead><tr><th>الدليل</th><th>الحجم</th><th></th></tr></thead>
                <tbody>{largest_html}</tbody>
            </table>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">📊 توزيع أنواع الملفات (حسب الحجم)</h3>
            <table class="data-table">
                <thead><tr><th>الامتداد</th><th>الحجم</th><th>العدد</th><th>المتوسط</th><th>عينات</th></tr></thead>
                <tbody>{types_html}</tbody>
            </table>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">📦 الملفات الكبيرة (>50MB)</h3>
            <table class="data-table">
                <thead><tr><th>الملف</th><th>الحجم</th><th>النوع</th><th>آخر تعديل</th></tr></thead>
                <tbody>{large_html if large_html else '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">لا توجد ملفات كبيرة</td></tr>'}</tbody>
            </table>
            
            <div class="divider"></div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">🔁 الملفات المكررة</h3>
            <table class="data-table">
                <thead><tr><th>الحجم</th><th>الأصلي</th><th>المكرر</th><th>MB</th></tr></thead>
                <tbody>{dupes_html if dupes_html else '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">لا توجد ملفات مكررة</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    """


def generate_diagnostics_section(diagnostics: list) -> str:
    if not diagnostics:
        return ''
    
    critical = [d for d in diagnostics if isinstance(d, dict) and d.get('severity') == 'critical']
    warnings = [d for d in diagnostics if isinstance(d, dict) and d.get('severity') == 'warning']
    info = [d for d in diagnostics if isinstance(d, dict) and d.get('severity') not in ('critical', 'warning')]
    
    rows_html = ""
    for d in diagnostics:
        if not isinstance(d, dict):
            continue
        severity = d.get('severity', 'info')
        badge_class = 'critical' if severity == 'critical' else 'warning' if severity == 'warning' else 'info'
        rows_html += f"""
        <tr>
            <td><span class="badge {badge_class}">{severity.upper()}</span></td>
            <td>{d.get('category', '')}</td>
            <td><strong>{d.get('title', '')}</strong></td>
            <td>{d.get('description', '')}</td>
            <td style="color: var(--accent-secondary);">{d.get('recommendation', '')}</td>
        </tr>
        """
    
    return f"""
    <div class="section">
        <div class="section-title">🔍 System Diagnostics</div>
        <div class="section-content">
            <div class="cards-grid" style="margin-bottom: 20px;">
                <div class="summary-card health-{'critical' if critical else 'warning' if warnings else 'good'}">
                    <div class="icon">{'🔴' if critical else '🟡' if warnings else '🟢'}</div>
                    <div class="value">{len(critical)}</div>
                    <div class="label">مشاكل حرجة</div>
                </div>
                <div class="summary-card health-warning">
                    <div class="icon">⚠️</div>
                    <div class="value">{len(warnings)}</div>
                    <div class="label">تحذيرات</div>
                </div>
                <div class="summary-card">
                    <div class="icon">ℹ️</div>
                    <div class="value">{len(info)}</div>
                    <div class="label">معلومات</div>
                </div>
            </div>
            
            <table class="data-table">
                <thead><tr><th>الخطورة</th><th>الفئة</th><th>المشكلة</th><th>الوصف</th><th>التوصية</th></tr></thead>
                <tbody>{rows_html if rows_html else '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary)">لا توجد مشاكل — النظام بحالة جيدة! ✅</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    """


def generate_windows_logs_section(logs_data: dict) -> str:
    if not logs_data:
        return ''
    
    all_events = []
    for evt in logs_data.get('system_events', []):
        if isinstance(evt, dict):
            evt['log_source'] = 'System'
            all_events.append(evt)
    for evt in logs_data.get('application_events', []):
        if isinstance(evt, dict):
            evt['log_source'] = 'Application'
            all_events.append(evt)
    
    all_events.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    summary = logs_data.get('summary', {})
    sys_sum = summary.get('System', {})
    app_sum = summary.get('Application', {})
    
    events_html = ""
    for evt in all_events[:50]:
        level = evt.get('level', 'information').lower()
        badge_class = 'critical' if level == 'critical' else 'error' if level == 'error' else 'warning' if level == 'warning' else 'info'
        msg = (evt.get('message', '') or '')[:120]
        events_html += f"""
        <tr>
            <td>{evt.get('time', '')[:19]}</td>
            <td><span class="badge {badge_class}">{level.upper()[:4]}</span></td>
            <td>{evt.get('id', '')}</td>
            <td>{evt.get('log_source', '')}</td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">{evt.get('provider', '')[:30]}</td>
            <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{msg}</td>
        </tr>
        """
    
    return f"""
    <div class="section">
        <div class="section-title">📋 Windows Event Logs</div>
        <div class="section-content">
            <div class="cards-grid" style="margin-bottom: 20px;">
                <div class="info-card">
                    <div class="card-title">System Events</div>
                    <div class="card-value">{sys_sum.get('error', 0) + sys_sum.get('critical', 0)} خطأ</div>
                    <div class="card-sub">تحذيرات: {sys_sum.get('warning', 0)}</div>
                </div>
                <div class="info-card">
                    <div class="card-title">Application Events</div>
                    <div class="card-value">{app_sum.get('error', 0) + app_sum.get('critical', 0)} خطأ</div>
                    <div class="card-sub">تحذيرات: {app_sum.get('warning', 0)}</div>
                </div>
                <div class="info-card">
                    <div class="card-title">إجمالي الأحداث</div>
                    <div class="card-value">{len(all_events)}</div>
                    <div class="card-sub">آخر 24 ساعة</div>
                </div>
            </div>
            
            <h3 style="color: var(--text-primary); font-size: 16px; margin-bottom: 15px;">📜 آخر 50 حدث</h3>
            <table class="data-table">
                <thead><tr><th>الوقت</th><th>المستوى</th><th>ID</th><th>المصدر</th><th>المزود</th><th>الرسالة</th></tr></thead>
                <tbody>{events_html if events_html else '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary)">لا توجد أحداث</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    """


def generate_footer(timestamp: datetime) -> str:
    return f"""
    <div class="report-footer">
        <p>تم إنشاء هذا التقرير بواسطة <strong>SystemScope v1.0</strong></p>
        <p>© {timestamp.year} — تحليل شامل للنظام بدون اتصال بالإنترنت</p>
    </div>
    """