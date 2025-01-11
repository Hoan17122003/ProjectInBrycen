import streamlit as st
import main_page
# Hàm xác thực người dùng
def authenticate(username, password):
    # Giả sử bạn có một danh sách người dùng đã đăng ký
    # Bạn có thể thay thế phần này với cơ sở dữ liệu thực tế
    valid_users = {"admin": "admin", "user": "user"}
    
    if username in valid_users and valid_users[username] == password:
        return True
    else:
        return False

def login_page():
    col_left , col_main, col_right = st.columns([1, 1, 1]) 
    with col_main:
        st.title("Trang Đăng Nhập")

        # Nhập tên người dùng và mật khẩu
        username = st.text_input("Tên người dùng")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if authenticate(username, password):
                st.session_state.logged_in = True  # Thiết lập trạng thái đăng nhập
                st.session_state.username = username
                st.session_state.page = "main_page"  # Chuyển đến trang chính
                st.rerun()  # Làm mới trang
            else:
                st.error("Tên người dùng hoặc mật khẩu không đúng!")

# Kiểm tra xem người dùng đã đăng nhập chưa
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login_page()  # Hiển thị trang đăng nhập nếu chưa đăng nhập
else:
    # Điều hướng đến các trang khác
    if st.session_state.page == "main_page":
        main_page.show_main_page()
