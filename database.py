import sqlite3
import os
from datetime import datetime

DB_PATH = "/storage/emulated/0/kasir_app/kasir.db"

def connect():
    os.makedirs("/storage/emulated/0/kasir_app", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = connect()
    c = conn.cursor()

    # Tabel users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Tabel products
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT,
        name TEXT,
        price INTEGER,
        stock INTEGER
    )
    """)

    # Tabel sales
    c.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total INTEGER,
        date TEXT
    )
    """)

    # User default
    c.execute(
        "INSERT OR IGNORE INTO users(username,password,role) VALUES('admin','admin','admin')"
    )
    c.execute(
        "INSERT OR IGNORE INTO users(username,password,role) VALUES('kasir','123','kasir')"
    )

    conn.commit()
    conn.close()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")