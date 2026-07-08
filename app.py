import streamlit as st
import sqlite3
import pandas as pd

# Cấu hình trang Web
st.set_page_config(page_title="HRIMS - Hệ thống Quản lý Nhân sự", layout="wide")

def connect_db():
    return sqlite3.connect("hrims.db")

# --- BỔ SUNG: Hàm tự động tạo bảng và nạp dữ liệu mẫu trên Server Online ---
def init_db_online():
    conn = connect_db()
    cursor = conn.cursor()
    
    # 1. Tạo bảng Departments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        dep_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dep_name TEXT NOT NULL UNIQUE
    )
    """)
    
    # 2. Tạo bảng Employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        dep_id INTEGER,
        salary REAL NOT NULL,
        FOREIGN KEY (dep_id) REFERENCES Departments(dep_id)
    )
    """)
    
    # 3. Nạp dữ liệu phòng ban mẫu nếu bảng trống
    cursor.execute("SELECT COUNT(*) FROM Departments")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT OR IGNORE INTO Departments (dep_name) VALUES (?)", 
                           [("Nhân Sự",), ("Công Nghệ",), ("Kinh Doanh",)])
    
    conn.commit()
    conn.close()

# --- GỌI HÀM KHỞI TẠO NGAY KHI TRANH WEB CHẠY ---
init_db_online()

# Hàm lấy danh sách phòng ban làm danh mục lựa chọn (Giữ nguyên cấu trúc cũ)
def get_departments():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM Departments", conn)
    conn.close()
    return df
