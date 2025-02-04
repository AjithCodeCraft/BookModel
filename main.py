from fastapi.responses import FileResponse
from PyPDF2 import PdfReader
import os
import uvicorn
from pydantic_settings import BaseSettings
import pyttsx3
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load settings
class Settings(BaseSettings):
    PORT: int = 8000
    ENV: str = "development"
    BASE_URL: str = "http://localhost:3000"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests only from your React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
settings = Settings()

# Directory to save temporary files
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
from fastapi import FastAPI, File, UploadFile, HTTPException

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)   
engine.setProperty('volume', 5.0)  # Set volume to maximum

# Function to generate audio
def generate_audio(text: str, output_path: str):
    """Generate speech from text using pyttsx3 and save as a .wav file."""
    try:
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        print(f"Audio generated successfully at {output_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}"
                            )
    


# Upload PDF endpoint
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"message": "PDF uploaded successfully", "file_path": file_path}

# Read PDF page and generate audio endpoint
@app.get("/read-page/")
async def read_page(file_path: str, page_number: int):
    try:
        reader = PdfReader(file_path)
        
        # Ensure page number is valid
        if page_number < 1 or page_number > len(reader.pages):
            raise HTTPException(status_code=400, detail="Invalid page number")
        
        page_text = reader.pages[page_number - 1].extract_text()
        if not page_text.strip():
            raise HTTPException(status_code=400, detail="No readable text on the page")
        
        audio_path = os.path.join(UPLOAD_DIR, f"page_{page_number}.wav")
        
        # Generate audio
        generate_audio(page_text, audio_path)
        
        return FileResponse(audio_path, media_type="audio/wav", filename=f"page_{page_number}.wav")
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# Root endpoint
@app.get("/")
def root():
    return {"message": "Audiocooker API is running"}

# Run the application
if __name__ == "__main__":
    port = 5001
    debug = settings.ENV == "development"
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        reload=debug
    )
