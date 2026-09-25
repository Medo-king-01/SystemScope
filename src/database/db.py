import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent.parent / 'systemscope.db'

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, cpu_percent REAL, ram_percent REAL, ram_total INTEGER, gpu_name TEXT, gpu_utilization INTEGER, gpu_temp REAL)''')
    conn.commit()
    conn.close()

def save_snapshot(data):
    conn = get_connection()
    conn.execute('INSERT INTO snapshots (timestamp, cpu_percent, ram_percent, ram_total, gpu_name, gpu_utilization, gpu_temp) VALUES (?, ?, ?, ?, ?, ?, ?)', (data.get('timestamp'), data.get('cpu_percent'), data.get('ram_percent'), data.get('ram_total'), data.get('gpu_name'), data.get('gpu_utilization'), data.get('gpu_temp')))
    conn.commit()
    conn.close()

def get_snapshots(limit=100):
    conn = get_connection()
    rows = conn.execute('SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]