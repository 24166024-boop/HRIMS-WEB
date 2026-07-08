import sqlite3

def connect_db():
    """Kết nối tới cơ sở dữ liệu SQLite"""
    return sqlite3.connect("hr_management.db")

def init_database():
    """Khởi tạo cấu trúc các bảng CSDL quan hệ chi tiết cho HRIMS"""
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Tạo bảng Phòng Ban
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_name TEXT NOT NULL UNIQUE
    )
    """)

    # 2. Tạo bảng Nhân Viên (Liên kết với Phòng ban qua department_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        department_id INTEGER,
        basic_salary REAL NOT NULL,
        FOREIGN KEY (department_id) REFERENCES Departments(department_id)
    )
    """)

    # 3. Tạo bảng Lương Chi Tiết (Liên kết với Nhân viên)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Payroll (
        payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month_year TEXT NOT NULL,
        work_days INTEGER NOT NULL,
        bonus REAL DEFAULT 0,
        deductions REAL DEFAULT 0,
        net_salary REAL NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES Employees(employee_id) ON DELETE CASCADE
    )
    """)

    # Thêm dữ liệu phòng ban mẫu nếu bảng trống
    cursor.execute("SELECT COUNT(*) FROM Departments")
    if cursor.fetchone()[0] == 0:
        departments = [("Phòng Nhân Sự",), ("Phòng Công Nghệ",), ("Phòng Kinh Doanh",)]
        cursor.executemany("INSERT INTO Departments (department_name) VALUES (?)", departments)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Khởi tạo Cơ sở dữ liệu HRIMS thành công!")