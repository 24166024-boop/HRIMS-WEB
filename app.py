import streamlit as st
import sqlite3
import pandas as pd

# Cấu hình trang Web (Luôn phải đặt đầu tiên)
st.set_page_config(page_title="HRIMS - Hệ thống Quản lý Nhân sự", layout="wide")

def connect_db():
    return sqlite3.connect("hrims.db")

# --- 1. ĐỊNH NGHĨA HÀM KHỞI TẠO CSDL TRƯỚC ---
def init_db_online():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Tạo bảng Departments nếu chưa có
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        dep_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dep_name TEXT NOT NULL UNIQUE
    )
    """)
    
    # Tạo bảng Employees nếu chưa có
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
    
    # Nạp dữ liệu mẫu nếu bảng trống
    cursor.execute("SELECT COUNT(*) FROM Departments")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT OR IGNORE INTO Departments (dep_name) VALUES (?)", 
                           [("Nhân Sự",), ("Công Nghệ",), ("Kinh Doanh",)])
    
    conn.commit()
    conn.close()

# --- 2. ÉP HỆ THỐNG CHẠY HÀM KHỞI TẠO NGAY TẠI ĐÂY ---
init_db_online()

# --- 3. SAU ĐÓ MỚI ĐỊNH NGHĨA HÀM ĐỌC DỮ LIỆU ---
def get_departments():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM Departments", conn)
    conn.close()
    return df

# --- 4. CÁC ĐOẠN CODE PHÍA DƯỚI GIỮ NGUYÊN ---
menu = st.sidebar.selectbox("CHỨC NĂNG HỆ THỐNG", 
    ["1. Tổng quan Dashboard", "2. Thêm nhân viên", "3. Danh sách & Xử lý (CRUD)", "4. Xuất dữ liệu báo cáo"])

# Bây giờ gọi hàm này sẽ KHÔNG bao giờ bị lỗi nữa vì bảng đã được tạo ở trên
df_deps = get_departments()

# (Giữ nguyên toàn bộ các phân hệ if/elif hiển thị Dashboard phía dưới...)
