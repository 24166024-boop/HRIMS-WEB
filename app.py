import streamlit as st
import sqlite3
import pandas as pd

# =================================================================
# 1. CẤU HÌNH TRANG WEB (BẮT BUỘC ĐẶT ĐẦU TIÊN)
# =================================================================
st.set_page_config(
    page_title="HRIMS - Hệ thống Quản lý Nhân sự", 
    page_icon="📊",
    layout="wide"
)

# Hàm kết nối CSDL SQLite
def connect_db():
    return sqlite3.connect("hrims.db")

# =================================================================
# 2. KHỞI TẠO CẤU TRÚC CSDL TỰ ĐỘNG (DÀNH CHO SERVER ONLINE)
# =================================================================
def init_db_online():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Tạo bảng Departments (Phòng ban) nếu chưa tồn tại
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        dep_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dep_name TEXT NOT NULL UNIQUE
    )
    """)
    
    # Tạo bảng Employees (Nhân viên) nếu chưa tồn tại
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
    
    # Nạp dữ liệu phòng ban mẫu nếu bảng hoàn toàn trống
    cursor.execute("SELECT COUNT(*) FROM Departments")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT OR IGNORE INTO Departments (dep_name) VALUES (?)", 
                           [("Nhân Sự",), ("Công Nghệ",), ("Kinh Doanh",), ("Kế Toán",)])
        
    conn.commit()
    conn.close()

# Kích hoạt hàm khởi tạo ngay khi ứng dụng load
init_db_online()

# =================================================================
# 3. CÁC HÀM TRUY VẤN DỮ LIỆU (ĐỌC / GHI CSDL)
# =================================================================
def get_departments():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM Departments", conn)
    conn.close()
    return df

def get_employees_with_dept():
    conn = connect_db()
    query = """
    SELECT e.emp_id, e.name, e.email, d.dep_name, e.salary 
    FROM Employees e
    LEFT JOIN Departments d ON e.dep_id = d.dep_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Lấy danh sách phòng ban để làm danh mục chọn chung cho toàn bộ app
df_deps = get_departments()

# =================================================================
# 4. GIAO DIỆN THANH ĐIỀU HƯỚNG (SIDEBAR)
# =================================================================
cac_chuc_nang = [
    "1. Tổng quan Dashboard", 
    "2. Thêm nhân viên", 
    "3. Danh sách & Xử lý (CRUD)", 
    "4. Xuất dữ liệu báo cáo"
]

st.sidebar.markdown("## 🏢 MENU QUẢN LÝ")
menu = st.sidebar.selectbox("CHỨC NĂNG HỆ THỐNG", cac_chuc_nang)

# Lấy vị trí Index của menu để xử lý rẽ nhánh giao diện (Tránh lỗi sai chính tả)
menu_index = cac_chuc_nang.index(menu)

# =================================================================
# 5. XỬ LÝ ĐIỀU HƯỚNG HIỂN THỊ CHI TIẾT THEO CHỨC NĂNG
# =================================================================

# --- PHÂN HỆ 1: TỔNG QUAN DASHBOARD ---
if menu_index == 0:
    st.title("📊 Tổng Quan Dashboard")
    st.write("---")
    
    df_emp = get_employees_with_dept()
    total_emp = len(df_emp)
    total_dep = len(df_deps)
    
    # Hiển thị các khối chỉ số tổng quan (Metrics)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số nhân sự", f"{total_emp} người")
    with col2:
        st.metric("Tổng số phòng ban", f"{total_dep} phòng")
    with col3:
        total_salary = df_emp['salary'].sum() if total_emp > 0 else 0
        st.metric("Tổng quỹ lương", f"{total_salary:,.0f} VNĐ")
        
    st.write("### 📈 Biểu đồ phân bổ nhân sự theo phòng ban")
    if total_emp > 0:
        dept_counts = df_emp['dep_name'].value_counts()
        st.bar_chart(dept_counts)
    else:
        st.info("Hệ thống chưa có nhân viên nào để vẽ biểu đồ. Hãy qua tab thêm nhân viên nhé!")

# --- PHÂN HỆ 2: THÊM NHÂN VIÊN MỚI ---
elif menu_index == 1:
    st.title("➕ Thêm Nhân Viên Mới Vào Hệ Thống")
    st.write("---")
    
    with st.form("add_employee_form", clear_on_submit=True):
        name = st.text_input("Họ và tên nhân viên:")
        email = st.text_input("Địa chỉ Email:")
        
        # Lấy list tên phòng ban từ database đổ vào selectbox
        dept_options = df_deps['dep_name'].tolist()
        selected_dept_name = st.selectbox("Chọn phòng ban trực thuộc:", dept_options)
        
        salary = st.number_input("Mức lương công tác (VNĐ):", min_value=0, step=500000)
        
        submit_btn = st.form_submit_button("Lưu thông tin")
        
        if submit_btn:
            if name and email:
                # Tìm dep_id tương ứng với dep_name được chọn
                dep_id = int(df_deps[df_deps['dep_name'] == selected_dept_name]['dep_id'].values[0])
                
                try:
                    conn = connect_db()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Employees (name, email, dep_id, salary) VALUES (?, ?, ?, ?)",
                                   (name, email, dep_id, salary))
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 Đã thêm thành công nhân sự: {name}")
                except sqlite3.IntegrityError:
                    st.error("❌ Email này đã tồn tại trên hệ thống, vui lòng kiểm tra lại!")
            else:
                st.warning("⚠️ Vui lòng điền đầy đủ Họ tên và Email!")

# --- PHÂN HỆ 3: DANH SÁCH & XỬ LÝ DỮ LIỆU (CRUD) ---
elif menu_index == 2:
    st.title("📋 Danh Sách Nhân Viên & Quản Lý Dữ Liệu")
    st.write("---")
    
    df_emp = get_employees_with_dept()
    
    if len(df_emp) > 0:
        # Thay đổi tiêu đề hiển thị cho đẹp
        df_display = df_emp.rename(columns={
            'emp_id': 'Mã NV', 'name': 'Họ và tên', 'email': 'Email', 
            'dep_name': 'Phòng ban', 'salary': 'Lương (VNĐ)'
        })
        st.dataframe(df_display, use_container_width=True)
        
        # Chức năng xóa nhân sự nhanh
        st.write("### 🗑️ Xóa nhân sự khỏi hệ thống")
        emp_ids = df_emp['emp_id'].tolist()
        selected_del_id = st.selectbox("Chọn mã nhân viên cần xóa:", emp_ids)
        
        if st.button("Xác nhận xóa nhân viên", type="primary"):
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Employees WHERE emp_id = ?", (selected_del_id,))
            conn.commit()
            conn.close()
            st.success("💥 Đã xóa nhân viên thành công!")
            st.rerun() # Tải lại trang để cập nhật bảng dữ liệu mới
    else:
        st.info("Hiện tại danh sách nhân viên đang trống!")

# --- PHÂN HỆ 4: XUẤT DỮ LIỆU BÁO CÁO ---
elif menu_index == 3:
    st.title("📥 Xuất Dữ Liệu & Báo Cáo Nhân Sự")
    st.write("---")
    
    df_emp = get_employees_with_dept()
    
    if len(df_emp) > 0:
        st.write("Hệ thống đã chuẩn bị xong file báo cáo tổng hợp nhân sự hiện tại dưới dạng định dạng chuẩn CSV.")
        
        # Chuyển đổi Dataframe thành dữ liệu CSV mã hóa UTF-8 để tải xuống
        csv_data = df_emp.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Bấm để Tải Xuống File Báo Cáo (.CSV)",
            data=csv_data,
            file_name="Bao_cao_nhan_su_HRIMS.csv",
            mime="text/csv"
        )
    else:
        st.warning("Không có dữ liệu nhân sự để kết xuất báo cáo!")
