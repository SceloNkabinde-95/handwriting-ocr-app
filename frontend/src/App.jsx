import React, { useState } from 'react'
import axios from 'axios'
import jsPDF from 'jspdf'

export default function App() {
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post('http://localhost:8000/ocr', formData)
      setText(res.data.text)
    } catch (err) {
      console.error(err)
      setError('Failed to process file.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    const pdf = new jsPDF()
    pdf.text(text, 10, 10)
    pdf.save('handwritten_text.pdf')
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>📝 Handwriting OCR</h1>

      <input type="file" accept=".jpg,.jpeg,.png,.pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Processing...' : 'Upload & Extract Text'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {text && (
        <>
          <h2>Recognized Text</h2>
          <textarea
            rows="10"
            cols="60"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <br />
          <button onClick={handleDownload}>Download PDF</button>
        </>
      )}
    </div>
  )
}
