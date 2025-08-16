from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./documents.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(String)
    upload_time = Column(DateTime, default=datetime.now)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app default port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        return {"message": "Only .txt files are allowed"}

    content = await file.read()
    content_str = content.decode("utf-8")

    db = SessionLocal()
    try:
        db_document = Document(filename=file.filename, content=content_str)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return {"message": "File uploaded successfully", "filename": db_document.filename, "upload_time": db_document.upload_time}
    finally:
        db.close()
