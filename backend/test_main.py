from fastapi.testclient import TestClient
import os
import pytest
import io
from PyPDF2 import PdfWriter, PdfReader
from docx import Document as DocxDocument
from sqlalchemy.orm import sessionmaker # Import sessionmaker explicitly
from unittest.mock import patch, MagicMock

# Patch the database URL before importing main to ensure in-memory database for tests
with patch('main.SQLALCHEMY_DATABASE_URL', "sqlite:///:memory:"):
    from main import app, SessionLocal, Base, Document, PyPDF2, DocxDocument as MainDocxDocument, get_db, engine as main_engine # Import main's engine for metadata ops

@pytest.fixture(name="db_session", scope="function")
def db_session_fixture():
    # Use the main app's engine which is now in-memory due to the patch
    # Drop and create tables for each test function to ensure isolation
    Base.metadata.drop_all(bind=main_engine)
    Base.metadata.create_all(bind=main_engine)

    db = SessionLocal() # Use main's SessionLocal, now bound to in-memory
    try:
        yield db
    finally:
        db.close()
        # No need to dispose engine here as it's global and patched at import level

@pytest.fixture(name="client_with_db")
def client_with_db_fixture(db_session):
    # Patch get_db in main.py to yield our test session
    with patch('main.get_db', return_value=iter([db_session])):
        yield TestClient(app)

# Helper function to create a dummy file for testing (for .txt files that need disk access)
def create_dummy_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    return filename

# Helper function to clean up dummy files
def cleanup_dummy_files(*filenames):
    for filename in filenames:
        if os.path.exists(filename):
            os.remove(filename)

def test_health_check(client_with_db):
    response = client_with_db.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_txt_document(client_with_db):
    test_filename = "test_document.txt"
    test_content = "This is a test document in plain text."
    dummy_file_path = create_dummy_file(test_filename, test_content)
    try:
        with open(dummy_file_path, "rb") as f:
            response = client_with_db.post(
                "/upload", files={"file": (test_filename, f, "text/plain")}
            )
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["filename"] == test_filename
        assert "predicted_category" in response.json()
        assert "confidence_scores" in response.json()
    finally:
        cleanup_dummy_files(dummy_file_path)

@patch('main.PyPDF2') # Patch PyPDF2 where it's used in main.py
def test_upload_pdf_document(mock_pypdf2_module, client_with_db):
    test_filename = "test_document.pdf"
    
    # Configure the mock PdfReader class and its instances
    mock_pdf_reader_class = MagicMock() # This will be the mock for PyPDF2.PdfReader
    mock_pypdf2_module.PdfReader = mock_pdf_reader_class # Assign our mock to PyPDF2.PdfReader

    mock_reader_instance = mock_pdf_reader_class.return_value # This is the mock for PdfReader() instance
    mock_page = MagicMock() # Create a MagicMock for a single page
    mock_page.extract_text.return_value = "This is dummy text extracted from a PDF."
    
    # Mock the 'pages' attribute to behave like a list of mock pages
    mock_pages_list = MagicMock()
    mock_pages_list.__getitem__.side_effect = lambda x: mock_page if x == 0 else IndexError # Supports indexing
    mock_pages_list.__len__.return_value = 1 # Supports len()
    mock_pages_list.__iter__.return_value = iter([mock_page]) # Supports iteration
    
    mock_reader_instance.pages = mock_pages_list

    # Simulate a file upload with some bytes (content doesn't matter as extraction is mocked)
    pdf_file_content = b"dummy pdf content"
    
    try:
        response = client_with_db.post(
            "/upload", files={"file": (test_filename, io.BytesIO(pdf_file_content), "application/pdf")}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["filename"] == test_filename
        assert "predicted_category" in response.json()
        assert "confidence_scores" in response.json()
        mock_pdf_reader_class.assert_called_once() # Ensure PdfReader was called
        mock_page.extract_text.assert_called_once() # Ensure extract_text was called
    finally:
        pass # No file to cleanup for in-memory content

def test_upload_docx_document(client_with_db):
    test_filename = "test_document.docx"
    doc = MainDocxDocument() # Use the imported DocxDocument from main
    doc.add_paragraph("This is a test document in DOCX format with some words.")
    # Save to a BytesIO object to simulate file upload without writing to disk
    docx_stream = io.BytesIO()
    doc.save(docx_stream)
    docx_stream.seek(0) # Rewind to the beginning of the stream

    try:
        response = client_with_db.post(
            "/upload", files={"file": (test_filename, docx_stream, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["filename"] == test_filename
        assert "predicted_category" in response.json()
        assert "confidence_scores" in response.json()
    finally:
        pass # No file to cleanup for in-memory content

def test_upload_unsupported_file_type(client_with_db):
    test_filename = "test_image.jpg"
    # Providing dummy content directly as bytes
    dummy_file_content = b"dummy image content"
    try:
        response = client_with_db.post(
            "/upload", files={"file": (test_filename, io.BytesIO(dummy_file_content), "image/jpeg")}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Only .txt, .pdf, and .docx files are allowed"
    finally:
        pass # No file to cleanup for in-memory content

def test_get_documents_empty(client_with_db):
    response = client_with_db.get("/documents")
    assert response.status_code == 200
    assert response.json() == []

def test_get_documents_after_upload(client_with_db):
    test_filename = "test_get_doc.txt"
    test_content = "This document is for retrieval testing."
    dummy_file_path = create_dummy_file(test_filename, test_content)

    # Upload a document first
    try:
        with open(dummy_file_path, "rb") as f:
            upload_response = client_with_db.post(
                "/upload", files={"file": (test_filename, f, "text/plain")}
            )
        assert upload_response.status_code == 200

        # Now retrieve documents
        response = client_with_db.get("/documents")
        assert response.status_code == 200
        documents = response.json()
        assert len(documents) > 0
        found = False
        for doc in documents:
            if doc["filename"] == test_filename:
                found = True
                assert "id" in doc
                assert "upload_time" in doc
                assert "predicted_category" in doc
                assert "confidence_scores" in doc
                break
        assert found, f"Document {test_filename} not found in retrieved documents."
    finally:
        cleanup_dummy_files(dummy_file_path)
