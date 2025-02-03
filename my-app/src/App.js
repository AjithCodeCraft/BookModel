import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import { pdfjs } from "react-pdf"; // ✅ Import pdfjs
import AudioCooker from "./pages/mainpage/AudioCooker";

// ✅ Set PDF.js worker source
// pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AudioCooker />} />
      </Routes>
    </Router>
  );
}

export default App;
