import streamlit as st
import sqlite3
import pandas as pd

# Cấu hình trang Web
st.set_page_config(page_title="HRIMS - Hệ thống Quản lý Nhân sự", layout="wide")


def connect_db():
    return sqlite3.connect("hrims.db")


# Hàm lấy danh sách phòng ban làm danh mục lựa chọn
def get_departments():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM Departments", conn)
    conn.close()
    return df


# --- TIÊU ĐỀ CHÍNH ---
st.title("💼 HRIMS - Doanh nghiệp Quản lý Nhân sự")
st.markdown("---")

# --- THANH DIỀU HƯỚNG BÊN TRÁI (SIDEBAR) ---
menu = st.sidebar.selectbox("CHỨC NĂNG HỆ THỐNG",
                            ["1. Tổng quan Dashboard", "2. Thêm nhân viên", "3. Danh sách & Xử lý (CRUD)",
                             "4. Xuất dữ liệu báo cáo"])

# Lấy dữ liệu phòng ban để dùng chung
df_deps = get_departments()

# =================================================================
# PHÂN HỆ 1: TỔNG QUAN DASHBOARD
# =================================================================
if menu == "1. Tổng quan Dashboard":
    st.subheader("📊 Thống kê nhân sự tổng quan")

    conn = connect_db()
    df_emp = pd.read_sql_query("""
                               SELECT e.emp_id, e.name, e.email, d.dep_name, e.salary
                               FROM Employees e
                                        LEFT JOIN Departments d ON e.dep_id = d.dep_id
                               """, conn)
    conn.close()

    if df_emp.empty:
        st.info("Hệ thống hiện tại chưa có nhân viên nào. Vui lòng chọn tính năng 'Thêm nhân viên'.")
    else:
        # Hiển thị số liệu dạng thẻ chỉ số trực quan
        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng số nhân viên", f"{len(df_emp)} người")
        col2.metric("Tổng quỹ lương/tháng", f"{df_emp['salary'].sum():,.0f} VND")
        col3.metric("Mức lương trung bình", f"{df_emp['salary'].mean():,.0f} VND")

        st.write("#### Biểu đồ phân bổ lương theo phòng ban")
        # Biểu đồ cột trực quan
        st.bar_chart(data=df_emp, x="dep_name", y="salary", color="dep_name")

# =================================================================
# PHÂN HỆ 2: THÊM NHÂN VIÊN MỚI (CREATE)
# =================================================================
elif menu == "2. Thêm nhân viên":
    st.subheader("➕ Đăng ký tài khoản nhân viên mới")

    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Họ và tên nhân viên:")
        email = st.text_input("Địa chỉ Email:")

        # Dropdown chọn phòng ban trực quan từ CSDL
        dep_options = {row['dep_name']: row['dep_id'] for _, row in df_deps.iterrows()}
        selected_dep = st.selectbox("Thuộc phòng ban:", list(dep_options.keys()))

        salary = st.number_input("Mức lương cơ bản (VND):", min_value=0, step=1000000)

        submit_btn = st.form_submit_button("Lưu vào hệ thống")

        if submit_btn:
            if name and email:
                conn = connect_db()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO Employees (name, email, dep_id, salary) VALUES (?, ?, ?, ?)",
                                   (name, email, dep_options[selected_dep], salary))
                    conn.commit()
                    st.success(f"🎉 Đã thêm thành công nhân viên {name} vào hệ thống!")
                except Exception as e:
                    st.error(f"Lỗi: Email đã tồn tại hoặc dữ liệu sai định dạng. ({e})")
                finally:
                    conn.close()
            else:
                st.warning("Vui lòng điền đầy đủ Họ tên và Email!")

# =================================================================
# PHÂN HỆ 3: DANH SÁCH & XỬ LÝ (READ - UPDATE - DELETE)
# =================================================================
elif menu == "3. Danh sách & Xử lý (CRUD)":
    st.subheader("🔍 Danh sách nhân sự & Thao tác nhanh")

    conn = connect_db()
    df_emp = pd.read_sql_query("""
                               SELECT e.emp_id as 'Mã NV', e.name as 'Họ Tên', e.email as 'Email', d.dep_name as 'Phòng Ban', e.salary as 'Lương (VND)'
                               FROM Employees e
                                        LEFT JOIN Departments d ON e.dep_id = d.dep_id
                               """, conn)
    conn.close()

    if df_emp.empty:
        st.info("Chưa có dữ liệu.")
    else:
        # Tìm kiếm nhân viên trực quan (Filter)
        search_term = st.text_input("🔍 Nhập tên nhân viên cần tìm nhanh:")
        if search_term:
            df_filtered = df_emp[df_emp['Họ Tên'].str.contains(search_term, case=False, na=False)]
        else:
            df_filtered = df_emp

        # Hiển thị bảng dữ liệu lưới sang xịn mịn
        st.dataframe(df_filtered, use_container_width=True)

        st.markdown("---")
        st.write("#### 🛠️ Khu vực Xử lý nâng cao")

        col_edit, col_del = st.columns(2)

        # Tab cập nhật lương nhanh
        with col_edit:
            st.write("**Cập nhật mức lương**")
            emp_to_edit = st.selectbox("Chọn Mã NV cần sửa lương:", df_emp['Mã NV'].tolist())
            new_salary = st.number_input("Mức lương mới (VND):", min_value=0, step=500000)
            if st.button("Xác nhận đổi lương"):
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE Employees SET salary = ? WHERE emp_id = ?", (new_salary, emp_to_edit))
                conn.commit()
                conn.close()
                st.success("Đã cập nhật lương thành công! Vui lòng tải lại trang.")

        # Tab xóa nhân viên
        with col_del:
            st.write("**Sa thải / Xóa nhân viên**")
            emp_to_del = st.selectbox("Chọn Mã NV cần xóa khỏi công ty:", df_emp['Mã NV'].tolist())
            if st.button("⚠️ Xóa vĩnh viễn", type="primary"):
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Employees WHERE emp_id = ?", (emp_to_del,))
                conn.commit()
                conn.close()
                st.error(f"Đã xóa nhân viên có mã số {emp_to_del}!")

# =================================================================
# PHÂN HỆ 4: XUẤT DỮ LIỆU BÁO CÁO
# =================================================================
elif menu == "4. Xuất dữ liệu báo cáo":
    st.subheader("📥 Xuất dữ liệu nhân sự phục vụ thanh tra/kế toán")

    conn = connect_db()
    df_emp = pd.read_sql_query("SELECT * FROM Employees", conn)
    conn.close()

    if not df_emp.empty:
        # Chuyển đổi dữ liệu bảng thành chuỗi CSV định dạng chuẩn
        csv_data = df_emp.to_csv(index=False).encode('utf-8')

        st.write("Bấm vào nút dưới đây để tải file danh sách về máy tính:")
        # Nút bấm tải file tích hợp của Streamlit
        st.download_button(
            label="💾 Tải xuống File danh_sach_nhan_vien.csv",
            data=csv_data,
            file_name="danh_sach_nhan_vien.csv",
            mime="text/csv"
        )
    else:
        st.info("Chưa có dữ liệu để xuất file.")