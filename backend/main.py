from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from transformers import pipeline
import json

# Zero-shot classification model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = [
    "Technical Documentation",
    "Business Proposal",
    "Legal Document",
    "Academic Paper",
    "General Article",
    "Other"
]

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
    predicted_category = Column(String, nullable=True)
    confidence_scores = Column(String, nullable=True) # Stored as JSON string

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

    # Perform classification
    classification_results = classifier(content_str, candidate_labels)
    predicted_category = classification_results['labels'][0]
    confidence_scores = {
        label: score for label, score in zip(classification_results['labels'], classification_results['scores'])
    }

    db = SessionLocal()
    try:
        db_document = Document(
            filename=file.filename,
            content=content_str,
            predicted_category=predicted_category,
            confidence_scores=json.dumps(confidence_scores)
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return {
            "message": "File uploaded successfully",
            "filename": db_document.filename,
            "upload_time": db_document.upload_time,
            "predicted_category": db_document.predicted_category,
            "confidence_scores": json.loads(db_document.confidence_scores)
        }
    finally:
        db.close()

@app.get("/documents")
async def get_documents():
    db = SessionLocal()
    try:
        documents = db.query(Document).all()
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "upload_time": doc.upload_time,
                "predicted_category": doc.predicted_category,
                "confidence_scores": json.loads(doc.confidence_scores)
            }
            for doc in documents
        ]
    finally:
        db.close()
