import streamlit as st
import os
from extract import extract_graph_and_chunk, reload_neo4j, bot_response, del_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from file import FileBase
from chathistory import ChatBase
from sqlalchemy.ext.declarative import declarative_base

from config import CONFIG



# Tạo bảng nếu chưa tồn tại

# Cấu hình ban đầu
st.set_page_config(layout="wide")

# Khởi tạo session state để lưu trữ thông tin
if "pdf_files" not in st.session_state:
    st.session_state.pdf_files = CONFIG.pdfs
if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = ""
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0
if "messages" not in st.session_state:
    st.session_state.messages = []


def make_sidebar():
    with st.sidebar:
        st.header("Quản lý PDF")
        # uploaded_file = st.file_uploader("Tải lên PDF", type=["pdf"])
        uploaded_file = st.file_uploader("Tải lên PDF", type=["pdf"], key=st.session_state.file_uploader_key)
        # lấy từ session đăng nhập
        user_id = 1 
        if uploaded_file is not None:
            file_name = uploaded_file.name
            uploadir= os.path.join(CONFIG.output_db,uploaded_file.name.replace(".pdf","")) 
            file_path = os.path.join(uploadir, uploaded_file.name)
            if not os.path.exists(uploadir):
                os.makedirs(uploadir, exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.pdf_files[file_name] = extract_graph_and_chunk(file_path )
                st.success(f"Đã tải lên: {uploaded_file.name}")
            else:
                st.warning(f"Đã tồn tại: {uploaded_file.name}")

            st.session_state.file_uploader_key += 1
            st.rerun()

        st.subheader("Các PDF đã tải")

        for file_name in reversed(st.session_state.pdf_files):
            # Tạo button với nút "X" để xóa
            col1, col2 = st.columns([9, 1])  # Tạo 2 cột, cột đầu để chứa nút, cột thứ 2 để chứa nút xóa
            
            with col1:
                name_display = file_name if len(file_name) < 17 else file_name[:14] + "..."
                if file_name == st.session_state.selected_pdf:
                    # Nếu file được chọn, thay đổi màu sắc
                    st.markdown(f'''
                        <button style="background-color: #40bb45; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; width: 100%;">{name_display}</button>
                    ''', unsafe_allow_html=True)
                else:
                    # Nút bình thường khi không được chọn
                    if st.button(name_display) and file_name != st.session_state.selected_pdf:
                        reload_neo4j(file_name.replace(".pdf", ""))
                        st.session_state.selected_pdf = file_name
                        st.session_state.messages = []
                        st.rerun()
            
            with col2:
                # Nút "X" để xóa file
                if st.button(f"X", key=file_name):  # Tạo nút xóa cho mỗi file
                    # Xóa file khỏi danh sách và cập nhật lại
                    del st.session_state.pdf_files[file_name]
                    del_db(file_name.replace(".pdf", ""))
                    st.session_state.selected_pdf = None
                    st.session_state.messages = []
                    st.rerun()  # Làm mới trang để cập nhật danh sách PDF


def make_chat():

    st.markdown(
    """
    <style>
    .title {
        position: sticky;
        top: 0 /* 3.75rem; /* Khoảng cách từ trên cùng */
        left: 0;
        width: auto;
        background-color: #40bb45;
        color: white;
        padding: 10px 10px;
        margin-bottom: 20px;
        margin-top: 0px;
        text-align: left;
        z-index: 1000;
        border-bottom: 1px solid #ddd;
        font-size: 24px;
        font-weight: bold;
        border-radius: 7px;
    }

    </style>
    """,
    unsafe_allow_html=True
    )

    if st.session_state.selected_pdf:
        st.markdown('<div class="title">Trò chuyện với: {}</div>'.format(st.session_state.get('selected_pdf', 'PDF chưa chọn')), unsafe_allow_html=True)

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input(f"Hỏi tôi về nội dung của {st.session_state.selected_pdf}"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            response = bot_response(prompt)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

    elif len(st.session_state.pdf_files) > 0:
        st.info( "Vui lòng chọn một PDF.") 
    else:
        st.info("Vui lòng tải lên và chọn PDF để bắt đầu.")

def show_main_page():
    make_sidebar()
    make_chat()

if __name__ == "__main__":
    show_main_page()    