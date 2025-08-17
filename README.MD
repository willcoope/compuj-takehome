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
The frontend is developed using React, providing a component-based architecture for a modular and maintainable user interface. It communicates with the backend exclusively via RESTful API calls. State management is handled using React's `useState` and `useEffect` hooks. The UI includes a drag-and-drop area for document uploads, real-time feedback on upload status, and a dynamic list displaying classified documents with their predicted categories and confidence scores.

## ML Model Justification

For the zero-shot text classification, the `facebook/bart-large-mnli` model from the Hugging Face Transformers library was chosen.

**Reasons for this choice:**
*   **Zero-Shot Capability:** This model is specifically trained for Natural Language Inference (NLI) tasks, making it highly effective for zero-shot classification. It can classify text into categories it hasn't explicitly seen during training, which aligns perfectly with the requirement to classify documents into predefined categories without prior training data for those categories.
*   **Performance:** `bart-large-mnli` is a robust and widely-used model that generally provides good accuracy for classification tasks.
*   **Ease of Integration:** Hugging Face Transformers provides a user-friendly `pipeline` API, simplifying the integration of the model into the FastAPI backend.

**Alternatives Considered and Trade-offs:**
*   **Simpler Models (TF-IDF + Logistic Regression):** While easier to implement and less computationally intensive, these models typically require labeled training data for the specific categories. Given the zero-shot requirement, `bart-large-mnli` was a more suitable choice despite its larger size and higher computational demands. The trade-off was increased complexity and resource usage for better out-of-the-box classification performance without labeled data.
*   **Other Transformer Models (e.g., Smaller BERT variants):** Smaller models might offer faster inference times but could potentially sacrifice accuracy. `bart-large-mnli` strikes a good balance between performance and accuracy for this task. The current setup prioritizes classification quality, and if deployment to a resource-constrained environment were a concern, further optimization or a smaller model might be considered.

## Future Improvements

*   **Long Document Handling:** Implement chunking for very large documents to avoid exceeding the model's token limit and to potentially improve classification accuracy for extensive texts.
*   **Asynchronous ML Processing:** For very large files or high traffic, offloading the ML classification to a background task queue (e.g., Celery) would prevent blocking the main FastAPI event loop and improve responsiveness.
*   **User Authentication and Authorization:** Implement user accounts to allow users to manage their own documents and classifications.
*   **Advanced UI/UX:** Enhance the frontend with features like:
    *   Loading indicators during file upload and classification.
    *   Better visual feedback for errors.
    *   Search and filter capabilities for the document list.
    *   Pagination for large numbers of documents.
*   **Dockerization:** Provide Dockerfiles and a `docker-compose.yml` for easier setup and deployment, encapsulating both backend and frontend environments.
*   **More Comprehensive Testing:** Expand unit tests to include more edge cases, integration tests between frontend and backend, and potentially end-to-end tests.
*   **Configurable Model and Categories:** Allow the ML model and candidate labels to be configured externally, rather than hardcoded, for greater flexibility.
*   **Error Logging and Monitoring:** Implement robust logging for production environments and integrate with monitoring tools.
*   **Basic Statistics Dashboard:** Create a dedicated section in the UI to display insights like document distribution by type, upload trends, or confidence score distributions, as suggested in the bonus requirements.