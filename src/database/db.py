"""
SQLite Database Layer for SystemScope.
Handles schema creation and CRUD operations for system snapshots.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent.parent / "systemscope.db"


class Database:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                ram_usage REAL,
                ram_total_gb REAL,
                ram_used_gb REAL,
                gpu_usage REAL,
                gpu_vram_used_gb REAL,
                disk_total_gb REAL,
                disk_used_gb REAL,
                network_latency_ms REAL,
                network_packet_loss REAL,
                processes_count INTEGER,
                startup_items_count INTEGER,
                data_json TEXT
            );

            CREATE TABLE IF NOT EXISTS diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                recommendation TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            );

            CREATE TABLE IF NOT EXISTS top_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                pid INTEGER,
                name TEXT,
                cpu_percent REAL,
                memory_mb REAL,
                status TEXT,
                username TEXT,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            );

            CREATE TABLE IF NOT EXISTS startup_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                name TEXT,
                command TEXT,
                location TEXT,
                enabled INTEGER,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            );

            CREATE TABLE IF NOT EXISTS storage_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                path TEXT,
                size_gb REAL,
                file_type TEXT,
                is_old INTEGER,
                is_duplicate INTEGER,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            );

            CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp);
            CREATE INDEX IF NOT EXISTS idx_diagnostics_severity ON diagnostics(severity);
        """)

        self.conn.commit()

    def save_snapshot(self, data: dict) -> int:
        """Save a full system snapshot and return its ID."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        sys = data.get("system", {})
        cpu = sys.get("cpu", {})
        ram = sys.get("ram", {})
        gpu = sys.get("gpu", {})
        primary_gpu = gpu.get("primary_gpu", {})
        storage = data.get("storage", {})
        net = data.get("network", {})
        internet = net.get("internet", {})
        google_dns = internet.get("latency_google_dns", {})

        cursor.execute("""
            INSERT INTO snapshots (
                timestamp, cpu_usage, ram_usage, ram_total_gb, ram_used_gb,
                gpu_usage, gpu_vram_used_gb, disk_total_gb, disk_used_gb,
                network_latency_ms, network_packet_loss, processes_count,
                startup_items_count, data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now,
            cpu.get("cpu_usage_percent"),
            ram.get("usage_percent"),
            ram.get("total_gb"),
            ram.get("used_gb"),
            primary_gpu.get("gpu_utilization_percent"),
            primary_gpu.get("vram_used_mb"),
            None,  # disk_total_gb — extracted from storage.partitions
            None,  # disk_used_gb
            google_dns.get("avg_ms"),
            google_dns.get("packet_loss_percent"),
            len(sys.get("processes", [])),
            len(sys.get("startup_items", [])),
            json.dumps(data, ensure_ascii=False, default=str)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def save_diagnostic(self, snapshot_id: int, severity: str, category: str,
                        title: str, description: str, recommendation: str):
        """Save a diagnostic finding."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO diagnostics (snapshot_id, severity, category, title, description, recommendation, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (snapshot_id, severity, category, title, description, recommendation,
              datetime.now().isoformat()))
        self.conn.commit()

    def get_latest_snapshot(self) -> Optional[dict]:
        """Get the most recent snapshot."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM snapshots ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_recent_snapshots(self, limit: int = 50) -> list:
        """Get recent snapshots for trend analysis."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, cpu_usage, ram_usage, disk_used_gb, network_latency_ms
            FROM snapshots ORDER BY id DESC LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

    def get_diagnostics_history(self, severity: Optional[str] = None) -> list:
        """Get diagnostic history with optional severity filter."""
        cursor = self.conn.cursor()
        if severity:
            cursor.execute("""
                SELECT d.*, s.timestamp as snapshot_time
                FROM diagnostics d
                JOIN snapshots s ON d.snapshot_id = s.id
                WHERE d.severity = ? ORDER BY d.id DESC LIMIT 100
            """, (severity,))
        else:
            cursor.execute("""
                SELECT d.*, s.timestamp as snapshot_time
                FROM diagnostics d
                JOIN snapshots s ON d.snapshot_id = s.id
                ORDER BY d.id DESC LIMIT 100
            """)
        return [dict(r) for r in cursor.fetchall()]

    def cleanup_old_snapshots(self, days: int = 7):
        """Delete snapshots older than X days and vacuum the database."""
        cursor = self.conn.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM snapshots WHERE timestamp < ?", (cutoff,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Delete old diagnostics first (foreign key)
            cursor.execute("""
                DELETE FROM diagnostics WHERE snapshot_id IN
                (SELECT id FROM snapshots WHERE timestamp < ?)
            """, (cutoff,))
            # Delete old snapshots
            cursor.execute("DELETE FROM snapshots WHERE timestamp < ?", (cutoff,))
            self.conn.commit()
            # Vacuum to reclaim space
            self.conn.execute("VACUUM")
            return count
        return 0

    def close(self):
        if self.conn:
            self.conn.close()
