# Compu-j Takehome

This project consists of a FastAPI backend and a React frontend.

## How to Run the Application

To run this application, you need to start both the backend and the frontend servers.

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
    Leave this terminal running, or run it in the background.

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

Once both servers are running, open your web browser and navigate to `http://localhost:3000`. Open the browser's developer console (F12) and check the console logs. You should see `{"status": "ok"}` printed, indicating that the frontend is successfully communicating with the backend's `/health` endpoint.

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
    This will open an interactive test runner in your terminal. You can press `q` to quit.

## Architectural Decisions

### Backend (FastAPI)
The backend is built with FastAPI, chosen for its high performance, ease of use, and automatic API documentation (Swagger UI/ReDoc). SQLAlchemy is used as the ORM for database interactions, providing a robust and flexible way to manage the `documents.db` SQLite database. Pydantic models are extensively used for data validation and serialization, ensuring clear and consistent API request and response structures.

File handling for uploads is managed directly by FastAPI's `UploadFile` mechanism, and content extraction for `.txt`, `.pdf` (using `PyPDF2`), and `.docx` (using `python-docx`) files is performed server-side.

### Frontend (React)
The frontend is developed using React, providing a component-based architecture for a modular and maintainable user interface. It communicates with the backend exclusively via RESTful API calls. State management is handled using React's `useState` and `useEffect` hooks. The UI now includes:

*   **Document Upload:** A user-friendly drag-and-drop area, also clickable for file selection.
*   **Real-time Feedback:** A loading animation/message is displayed during document classification, and clear success/error alerts (dismissible) provide immediate feedback.
*   **Document List View:** A dynamic list displays previously uploaded documents, sorted by most recent upload time.
*   **Interactive Details:** Each document card is clickable to toggle a detailed view, revealing confidence scores for all categories in a clean, bar-chart-like visualization. A "Click for more details" prompt is shown when details are collapsed.
*   **Low Confidence Indication:** Documents classified as 'Other' (including those reclassified due to low confidence) are visually highlighted for easier identification.

### Error Handling and Logging

Robust error handling is implemented across both the backend and frontend to ensure a resilient application:

*   **Backend Error Handling:** The FastAPI backend handles invalid file types and errors during text extraction (PDFs, DOCX) by returning `400 Bad Request` responses with informative details. Database errors during saving or retrieval are caught, rolled back (for save operations), and return `500 Internal Server Error` responses.
*   **Backend Logging:** A comprehensive logging strategy is in place, using Python's `logging` module to capture `INFO`, `WARNING`, and `ERROR` level messages for critical operations, potential issues, and exceptions. This aids in debugging and monitoring.
*   **Frontend Error Display:** User-friendly and dismissible alert messages (styled for success and danger) are used to provide clear feedback on upload status and any errors encountered during the process.

## ML Model Justification

For the zero-shot text classification, the `facebook/bart-large-mnli` model from the Hugging Face Transformers library was chosen.

**Reasons for this choice:**
*   **Zero-Shot Capability:** This model is specifically trained for Natural Language Inference (NLI) tasks, making it highly effective for zero-shot classification. It can classify text into categories it hasn't explicitly seen during training, which aligns perfectly with the requirement to classify documents into predefined categories without prior training data for those categories.
*   **Performance:** `bart-large-mnli` is a robust and widely-used model that generally provides good accuracy for classification tasks.
*   **Ease of Integration:** Hugging Face Transformers provides a user-friendly `pipeline` API, simplifying the integration of the model into the FastAPI backend.

**Alternatives Considered and Trade-offs:**
*   **Simpler Models (TF-IDF + Logistic Regression):** While easier to implement and less computationally intensive, these models typically require labeled training data for the specific categories. Given the zero-shot requirement, `bart-large-mnli` was a more suitable choice despite its larger size and higher computational demands. The trade-off was increased complexity and resource usage for better out-of-the-box classification performance without labeled data.
*   **Other Transformer Models (e.g., Smaller BERT variants):** Smaller models might offer faster inference times but could potentially sacrifice accuracy. `bart-large-mnli` strikes a good balance between performance and accuracy for this task. The current setup prioritizes classification quality, and if deployment to a resource-constrained environment were a concern, further optimization or a smaller model might be considered.

### ML Pipeline Robustness Enhancements

To improve the robustness of the ML pipeline, especially for real-world document scenarios, the following features have been implemented:

*   **Text Chunking for Long Documents:** Documents are now chunked into smaller segments (`MAX_CHUNK_SIZE` characters with `CHUNK_OVERLAP` for context) before being fed to the classification model. The classification results from all chunks are then aggregated by averaging their confidence scores for each label. This prevents issues with models exceeding token limits and potentially improves accuracy for lengthy texts.
*   **Explicit Low Confidence Handling:** A `LOW_CONFIDENCE_THRESHOLD` (currently 0.45) has been introduced. If the model's top predicted category has a confidence score below this threshold, and it's not already 'Other', the document is reclassified to the 'Other' category. This helps in explicitly identifying documents where the model is uncertain. In the UI, documents classified as 'Other' (which now includes reclassified low-confidence documents) are visually highlighted with an orange border to indicate their potentially ambiguous nature.

## Future Improvements

*   **Basic Statistics Dashboard:** Consider adding a simple statistics dashboard to display insights like document distribution by type, upload trends over time, or confidence score distributions.
*   **Asynchronous ML Processing:** For very large files or high traffic, offloading the ML classification to a background task queue (e.g., Celery) would prevent blocking the main FastAPI event loop and improve responsiveness.
*   **User Authentication and Authorization:** Implement user accounts to allow users to manage their own documents and classifications.
*   **Advanced UI/UX:** Enhance the frontend with features like search and filter capabilities for the document list, and pagination for large numbers of documents.
*   **Dockerization:** Provide Dockerfiles and a `docker-compose.yml` for easier setup and deployment, encapsulating both backend and frontend environments.
*   **Comprehensive Testing:** Expand unit tests to include more edge cases, integration tests between frontend and backend, and potentially end-to-end tests.
*   **Configurable Model and Categories:** Allow the ML model and candidate labels to be configured externally, rather than hardcoded, for greater flexibility.
*   **Error Logging and Monitoring:** Implement robust logging for production environments and integrate with monitoring tools. (Note: Basic logging is already implemented, this refers to more advanced setup like external monitoring services).