from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

class ChatStorage:
    def __init__(self, db_url="sqlite:///chat_history.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def save_message(self, file_name, role, content):
        """Lưu tin nhắn vào database"""
        session = self.Session()
        try:
            chat_message = ChatHistory(
                file_name=file_name,
                role=role,
                content=content
            )
            session.add(chat_message)
            session.commit()
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            session.rollback()
            return False
        finally:
            session.close()
            
    def get_chat_history(self, file_name):
        """Lấy lịch sử chat của một file"""
        session = self.Session()
        try:
            history = session.query(ChatHistory)\
                .filter(ChatHistory.file_name == file_name)\
                .order_by(ChatHistory.timestamp)\
                .all()
            return [msg.to_dict() for msg in history]
        finally:
            session.close()
            
    def export_chat_history(self, file_name, export_dir="chat_exports"):
        """Xuất lịch sử chat ra file JSON"""
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        history = self.get_chat_history(file_name)
        export_path = os.path.join(export_dir, f"{file_name}_chat_history.json")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return export_path
    
    def import_chat_history(self, file_path):
        """Nhập lịch sử chat từ file JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        session = self.Session()
        try:
            for msg in history:
                chat_message = ChatHistory(
                    file_name=msg['file_name'],
                    role=msg['role'],
                    content=msg['content'],
                    timestamp=datetime.fromisoformat(msg['timestamp'])
                )
                session.add(chat_message)
            session.commit()
            return True
        except Exception as e:
            print(f"Error importing history: {e}")
            session.rollback()
            return False
        finally:
            session.close()