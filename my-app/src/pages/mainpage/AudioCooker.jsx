import { useState } from "react";
import axios from "axios";
import { PdfDocument } from "@ironsoftware/ironpdf";

export default function AudioCooker() {
  const [file, setFile] = useState(null);
  const [fileText, setFileText] = useState(""); // Extracted text
  const [audioSrc, setAudioSrc] = useState(null);

  const handleFileChange = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);

    try {
      const reader = new FileReader();
      reader.readAsArrayBuffer(selectedFile);
      reader.onloadend = async () => {
        const pdfDoc = await PdfDocument.fromBytes(new Uint8Array(reader.result));
        const text = await pdfDoc.extractText(); // Extract text
        setFileText(text);
      };
    } catch (error) {
      console.error("Error processing PDF:", error);
      alert("Failed to process PDF");
    }
  };

  const fetchAudio = async () => {
    if (!fileText) return alert("Extract text first");

    try {
      const response = await axios.post("http://127.0.0.1:5001/generate-audio", {
        text: fileText,
      }, { responseType: "blob" });

      setAudioSrc(URL.createObjectURL(response.data));
    } catch (error) {
      console.error("Error fetching audio:", error);
      alert("Failed to fetch audio");
    }
  };

  return (
    <div className="flex flex-col items-center p-5 space-y-4">
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <p className="mt-2 text-sm text-gray-600">Extracted Text: {fileText.slice(0, 100)}...</p>

      <button
        onClick={fetchAudio}
        className="px-6 py-3 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600"
      >
        Listen to Audio
      </button>

      {audioSrc && <audio controls src={audioSrc} className="mt-2" />}
    </div>
  );
}
