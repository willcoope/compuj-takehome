import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
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
  }, []);

  const handleDrop = async (event) => {
    event.preventDefault();
    event.stopPropagation();

    setMessage(''); // Clear previous messages

    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      const file = event.dataTransfer.files[0];
      if (file.name.endsWith('.txt')) {
        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData,
          });
          const data = await response.json();
          if (response.ok) {
            setMessage(`Success: ${data.message} - ${data.filename}`);
          } else {
            setMessage(`Error: ${data.message || response.statusText}`);
          }
        } catch (error) {
          console.error('Upload error:', error);
          setMessage('Failed to upload file.');
        }
      } else {
        setMessage('Only .txt files are allowed.');
      }
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
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
          style={{
            border: '2px dashed #ccc',
            padding: '20px',
            textAlign: 'center',
            width: '300px',
            minHeight: '100px',
            margin: '20px auto',
            color: '#ccc'
          }}
        >
          Drag and drop your .txt file here
        </div>
        {message && <p style={{ color: message.startsWith('Error') ? 'red' : 'green' }}>{message}</p>}
      </header>
    </div>
  );
}

export default App;
