import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [ocrText, setOcrText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setOcrText("");
    setErrorMsg("");
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setErrorMsg("");
      const response = await axios.post("http://localhost:8000/ocr", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data?.text) {
        setOcrText(response.data.text);
      } else {
        setErrorMsg("No text was recognized.");
      }
    } catch (err) {
      console.error(err);
      setErrorMsg("An error occurred during OCR.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1>📝 Handwriting OCR with Azure</h1>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "⏳ Processing..." : "📤 Upload & OCR"}
      </button>

      {errorMsg && <p style={styles.error}>{errorMsg}</p>}
      {ocrText && (
  <div style={styles.outputBox}>
    <h3>📝 Editable Recognized Text</h3>
    <textarea
      value={ocrText}
      onChange={(e) => setOcrText(e.target.value)}
      style={styles.textarea}
      rows={10}
    />
  </div>
)}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "600px",
    margin: "auto",
    padding: "2rem",
    fontFamily: "Arial, sans-serif",
    textAlign: "center",
  },
  outputBox: {
    marginTop: "2rem",
    padding: "1rem",
    backgroundColor: "#f8f8f8",
    border: "1px solid #ddd",
    borderRadius: "8px",
    whiteSpace: "pre-wrap",
    textAlign: "left",
  },
  error: {
    color: "red",
    marginTop: "1rem",
  },
};

export default App;
