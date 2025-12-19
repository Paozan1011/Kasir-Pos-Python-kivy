import sqlite3
import os
from datetime import datetime

DB_PATH = "kasir.db"

def connect():
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
    bayar INTEGER,
    kembalian INTEGER,
    date TEXT
    )
    """)

# Tabel sales_items (DETAIL BARANG PER TRANSAKSI)
    c.execute("""
    CREATE TABLE IF NOT EXISTS sales_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    product_name TEXT,
    price INTEGER,
    qty INTEGER,
    subtotal INTEGER,
    FOREIGN KEY (sale_id) REFERENCES sales(id)
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