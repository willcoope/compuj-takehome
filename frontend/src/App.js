import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [documents, setDocuments] = useState([]);
  const fileInputRef = useRef(null);

  const fetchDocuments = async () => {
    try {
      const response = await fetch('http://localhost:8000/documents');
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      } else {
        console.error('Failed to fetch documents:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  useEffect(() => {
    // Health check
    const url = 'http://localhost:8000/health';
    console.log(`Attempting to fetch from: ${url}`);
    fetch(url)
      .then(response => {
        console.log('Raw response:', response);
        return response.text();
      })
      .then(text => {
        try {
          const data = JSON.parse(text);
          console.log('Parsed data:', data);
        } catch (error) {
          console.error('Error parsing JSON:', error, 'Raw text:', text);
        }
      })
      .catch(error => console.error('Fetch error:', error));

    // Fetch documents on mount
    fetchDocuments();
  }, []);

  const handleFile = async (file) => {
    setMessage(''); // Clear previous messages

    const allowedExtensions = ['.txt', '.pdf', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop();

    if (allowedExtensions.includes(fileExtension)) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        if (response.ok) {
          setMessage(`Success: ${data.message} - ${data.filename}. Category: ${data.predicted_category}`);
          fetchDocuments(); // Refresh the list of documents
        } else {
          setMessage(`Error: ${data.message || response.statusText}`);
        }
      } catch (error) {
        console.error('Upload error:', error);
        setMessage('Failed to upload file.');
      }
    } else {
      setMessage('Only .txt, .pdf, and .docx files are allowed.');
    }
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      handleFile(event.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleFileInputChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      handleFile(event.target.files[0]);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <p>
          Document Uploader
        </p>
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={handleClick}
          style={{
            border: '2px dashed #ccc',
            padding: '20px',
            textAlign: 'center',
            width: '300px',
            minHeight: '100px',
            margin: '20px auto',
            color: '#ccc',
            cursor: 'pointer' // Add cursor pointer to indicate it's clickable
          }}
        >
          Drag and drop your .txt, .pdf, or .docx file here, or click to upload
        </div>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInputChange}
          style={{ display: 'none' }} // Hide the input
          accept=".txt,.pdf,.docx" // Specify accepted file types
        />
        {message && <p style={{ color: message.startsWith('Error') ? 'red' : 'green' }}>{message}</p>}

        <h2>Uploaded Documents</h2>
        {documents.length === 0 ? (
          <p>No documents uploaded yet.</p>
        ) : (
          <div style={{ width: '80%', margin: '20px auto', textAlign: 'left' }}>
            {documents.map((doc) => (
              <div key={doc.id} className="document-card">
                <h3>{doc.filename}</h3>
                <p><strong>Category:</strong> {doc.predicted_category}</p>
                <p><strong>Upload Time:</strong> {new Date(doc.upload_time).toLocaleString()}</p>
                <p><strong>Confidence Scores:</strong></p>
                <ul>
                  {Object.entries(doc.confidence_scores).map(([label, score]) => (
                    <li key={label}><span>{label}:</span> <span>{(score * 100).toFixed(2)}%</span></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
