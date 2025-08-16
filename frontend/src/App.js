import { useEffect } from 'react';
import './App.css';

function App() {
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

  return (
    <div className="App">
      <header className="App-header">
        <p>
          Document Uploader
        </p>
        <button>Upload Document</button>
      </header>
    </div>
  );
}

export default App;
