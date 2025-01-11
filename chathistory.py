from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from file import File
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ChatBase = declarative_base()

class ChatHistory(ChatBase):
    __tablename__ = 'chat_histories'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
# Kết nối tới MySQL
DATABASE_URL = "mysql+pymysql://root:HoanHa@localhost:3306/ChatBoxDB"
engine = create_engine( DATABASE_URL, echo=True, pool_pre_ping=True ) 
Base = declarative_base() 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ChatBase.metadata.create_all(engine)
    

def create_file(db,title:str, url:str):
    # userCheck = session.query(User).filter_by(user_id).first()
    # if not userCheck : 
    #     return "user không tồn tại"
    file = File(url=url, title=title)
    # file.user = userCheck
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