"use client";

import { useState } from "react";
import axios from "axios";
import { Document, Page, pdfjs } from "react-pdf";
import "tailwindcss/tailwind.css";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function Home() {
  const [file, setFile] = useState(null);
  const [filePath, setFilePath] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [numPages, setNumPages] = useState(null);
  const [audioSrc, setAudioSrc] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = "http://localhost:5001";

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a PDF file.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload-pdf/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setFilePath(response.data.file_path.replace("http://localhost:3000", "http://localhost:5001"));
    } catch (error) {
      console.error("Upload Error:", error);
      alert("Failed to upload PDF");
    }
  };

  const fetchPageAudio = async () => {
    if (!filePath) return alert("Please upload a PDF first.");

    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/read-page/`, {
        params: { file_path: filePath, page_number: pageNumber },
      });
      setAudioSrc(response.request.responseURL);
    } catch (error) {
      console.error("Error fetching audio:", error);
      alert("Failed to fetch audio");
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto p-6 text-center">
      <h1 className="text-4xl font-extrabold mb-6 text-gray-800">Upload and Read PDF</h1>

      <form onSubmit={handleUpload} className="mb-6 flex flex-col items-center gap-4">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
          required
          className="block w-full border border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button type="submit" className="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-all">Upload PDF</button>
      </form>

      {filePath && (
        <div>
          <Document file={filePath} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
            <Page pageNumber={pageNumber} className="border rounded-lg shadow-md p-4" />
          </Document>
          <p className="mt-4 text-lg font-medium text-gray-700">Page {pageNumber} of {numPages}</p>
          <div className="flex justify-center gap-4 mt-4">
            <button 
              onClick={() => setPageNumber((prev) => Math.max(prev - 1, 1))} 
              disabled={pageNumber <= 1}
              className="bg-gray-500 text-white py-2 px-6 rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-all"
            >
              Previous
            </button>
            <button 
              onClick={() => setPageNumber((prev) => Math.min(prev + 1, numPages))} 
              disabled={pageNumber >= numPages}
              className="bg-gray-500 text-white py-2 px-6 rounded-lg hover:bg-gray-600 transition-all"
            >
              Next
            </button>
            <button 
              onClick={fetchPageAudio} 
              className="bg-green-600 text-white py-2 px-6 rounded-lg hover:bg-green-700 transition-all"
            >
              {loading ? "Loading..." : "Play Audio"}
            </button>
          </div>
        </div>
      )}

      {audioSrc && (
        <audio controls autoPlay className="mt-6 w-full max-w-lg mx-auto">
          <source src={audioSrc} type="audio/mpeg" />
        </audio>
      )}
    </div>
  );
}