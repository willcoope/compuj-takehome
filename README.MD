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