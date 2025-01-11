from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
# Khởi tạo base
FileBase = declarative_base()

# Định nghĩa mô hình
class File(FileBase):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500))
    title = Column(String(100),unique = True)
    chat_history = relationship("chat_history",back_populates="files",cascade="all, delete-orphan")



# Kết nối tới MySQL
DATABASE_URL = "mysql+pymysql://root:HoanHa@localhost:3306/ChatBoxDB"
engine = create_engine( DATABASE_URL, echo=True, pool_pre_ping=True ) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# FileBase.metadata.create_all(engine)

# Tạo session và thêm dữ liệu
def create_file(db,title:str, url:str):
    # userCheck = session.query(User).filter_by(user_id).first()
    # if not userCheck : 
    #     return "user không tồn tại"
    file = File(url=url, title=title)
    db.add(file)
    db.commit()
    db.close()

def delete_file(db,title : str):
    # Xóa user và tự động xóa các bài viết liên kết
    fileCheck = db.query(File).filter_by(title).first()
    if fileCheck:
        db.delete(fileCheck)
        db.commit()
        print("Đã xóa file")
    else:
        print("Không tìm thấy user để xóa.")

    db.close()