# Compu-j Takehome

This project features a FastAPI backend and a React frontend.

## How to Run the Application

To run this application, both the backend and frontend servers need to be started.

### 1. Backend Setup and Run (FastAPI)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Set up a Python virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    # On Windows, activate with: .\venv\Scripts\activate
    # On macOS/Linux, activate with: source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    Keep this terminal running, or run it in the background.

### 2. Frontend Setup and Run (React)

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies (if you haven't already):**
    ```bash
    npm install
    ```

3.  **Start the React development server:**
    ```bash
    npm start
    ```

### 3. Verify Connection

Once both servers are running, open your web browser and navigate to `http://localhost:3000`. Open the browser's developer console (F12) and check the console logs. You should see `{"status": "ok"}` printed, confirming frontend-backend communication via the `/health` endpoint.

## How to Run Tests

### 1. Backend Tests (FastAPI)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Activate your virtual environment:**
    *   On Windows: `.\venv\Scripts\activate`
    *   On macOS/Linux: `source venv/bin/activate`

3.  **Run pytest:**
    ```bash
    pytest
    ```

### 2. Frontend Tests (React)

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Run the tests:**
    ```bash
    npm test
    ```
    This opens an interactive test runner in your terminal. Press `q` to quit.

## Architectural Decisions

### Backend (FastAPI)
The backend uses FastAPI, chosen for its strong performance, ease of use, and built-in API documentation (Swagger UI/ReDoc). SQLAlchemy manages database interactions with `documents.db` (SQLite), providing a robust ORM layer. Pydantic models validate and serialize data for consistent API structures.

File uploads are handled by FastAPI's `UploadFile` mechanism, with text content extracted server-side from `.txt`, `.pdf` (using `PyPDF2`), and `.docx` (using `python-docx`) files.

### Frontend (React)
The frontend, built with React, offers a modular and maintainable user interface. It communicates exclusively with the backend via RESTful API calls. React's `useState` and `useEffect` hooks manage component state. The UI features include:

*   **Document Upload:** A user-friendly drag-and-drop area, also clickable for file selection.
*   **Real-time Feedback:** A loading animation and clear, dismissible success/error alerts provide immediate feedback during document classification.
*   **Document List View:** Displays uploaded documents, sorted by most recent upload time.
*   **Interactive Details:** Each document card is clickable to toggle a detailed view, showing confidence scores in a bar-chart-like visualization. A "Click for more details" prompt indicates this functionality.
*   **Low Confidence Indication:** Documents classified as 'Other' (including those reclassified due to low confidence) are visually highlighted.

### Error Handling and Logging

Robust error handling is a core part of the application, ensuring resilience:

*   **Backend Error Handling:** The FastAPI backend handles invalid file types and text extraction errors by returning `400 Bad Request` responses. Database errors (save/retrieve) are caught, rolled back (for saves), and return `500 Internal Server Error` responses.
*   **Backend Logging:** Python's `logging` module captures `INFO`, `WARNING`, and `ERROR` messages for operations, potential issues, and exceptions, aiding debugging and monitoring.
*   **Frontend Error Display:** User-friendly and dismissible alerts (styled for success and danger) provide clear feedback on upload status and errors.

## ML Model Justification

For zero-shot text classification, the `facebook/bart-large-mnli` model from Hugging Face Transformers was selected.

**Reasons for this choice:**
*   **Zero-Shot Capability:** Ideal for classifying text into unseen categories, leveraging its Natural Language Inference (NLI) training.
*   **Performance:** A robust model offering good accuracy for classification.
*   **Ease of Integration:** Simplified via Hugging Face Transformers' `pipeline` API.

**Alternatives Considered and Trade-offs:**
*   **Simpler Models (TF-IDF + Logistic Regression):** While less computationally intensive, these require labeled training data. `bart-large-mnli` was preferred for its zero-shot ability, accepting higher resource use for out-of-the-box performance without labeled data.
*   **Other Transformer Models:** Smaller models offer faster inference but may sacrifice accuracy. `bart-large-mnli` balances quality and speed. For resource-constrained deployments, further optimization or a smaller model might be considered.

### ML Pipeline Robustness Enhancements

To enhance ML pipeline robustness for real-world documents:

*   **Text Chunking:** Long documents are split into chunks (`MAX_CHUNK_SIZE` characters with `CHUNK_OVERLAP`). Chunk classifications are averaged for overall confidence. This handles token limits and improves accuracy for long texts.
*   **Low Confidence Handling:** A `LOW_CONFIDENCE_THRESHOLD` (0.45) reclassifies documents with low top-category confidence to 'Other'. The UI highlights these documents.

## Future Improvements

*   **Basic Statistics Dashboard:** Insights like document distribution, upload trends, or confidence score distributions.
*   **Asynchronous ML Processing:** Offload heavy ML tasks to a background queue (e.g., Celery) for improved responsiveness.
*   **User Authentication/Authorization:** Implement user accounts for managing private documents.
*   **Advanced UI/UX:** Features like search/filter for the document list, and pagination.
*   **Dockerization:** Provide Dockerfiles and `docker-compose.yml` for easier setup and deployment.
*   **Comprehensive Testing:** Expand unit tests (more edge cases, integration, end-to-end).
*   **Configurable ML:** Allow external configuration of the ML model and candidate labels.
*   **Enhanced Logging/Monitoring:** Integrate with external monitoring tools for production environments.