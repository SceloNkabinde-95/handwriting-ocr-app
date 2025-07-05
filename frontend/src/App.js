import React, { useState } from 'react';
import axios from 'axios';
import { jsPDF } from 'jspdf';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setText('');
    setError('');
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await axios.post('http://localhost:8000/ocr', formData);
      setText(res.data.text);
    } catch (err) {
      setError('Failed to process file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    const lines = doc.splitTextToSize(text, 180);
    doc.text(lines, 10, 10);
    doc.save('handwritten_text.pdf');
  };

  return (
    <div className="App">
      <h1>📝 Handwriting OCR</h1>

      <input type="file" accept=".png,.jpg,.jpeg,.pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading || !file}>
        {loading ? 'Processing...' : 'Upload & Extract Text'}
      </button>

      {error && <p className="error">{error}</p>}

      {text && (
        <>
          <textarea
            rows="10"
            value={text}
            onChange={(e) => setText(e.target.value)}
          ></textarea>
          <button onClick={handleDownloadPDF}>Download PDF</button>
        </>
      )}
    </div>
  );
}

export default App;
