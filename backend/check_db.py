from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./documents.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(String)
    upload_time = Column(DateTime)

def check_documents_in_db():
    db = SessionLocal()
    try:
        documents = db.query(Document).all()
        if not documents:
            print("No documents found in the database.")
        else:
            print("Documents in database:")
            for doc in documents:
                print(f"ID: {doc.id}, Filename: {doc.filename}, Upload Time: {doc.upload_time}, Content Length: {len(doc.content)} bytes")
    finally:
        db.close()

if __name__ == "__main__":
    check_documents_in_db()
