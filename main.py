from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader
import os
import uvicorn
from pydantic_settings import BaseSettings
import outetts

app = FastAPI()

# Load settings
class Settings(BaseSettings):
    PORT: int = 8000
    ENV: str = "development"
    BASE_URL: str = "http://localhost:8000"

settings = Settings()

# Directory to save temporary files
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize OuteTTS model
model_config = outetts.HFModelConfig_v2(
    model_path="OuteAI/OuteTTS-0.3-1B",
    tokenizer_path="OuteAI/OuteTTS-0.3-1B"
)
interface = outetts.InterfaceHF(model_version="0.3", cfg=model_config)

# Load default male speaker
interface.print_default_speakers()
speaker = interface.load_default_speaker(name="en_male_1")

# Function to clean text
def clean_text(text: str) -> str:
    """Clean and preprocess text to add natural pauses and improve flow."""
    text = text.replace(".", "....")  # Adds a small pause at the end of sentences
    text = text.replace(",", ",...")  # Adds a slight pause after commas
    text = text.replace("!", "!...")  # Adds emphasis and pause at exclamation
    text = text.replace("?", "?... hmm...")  # Adds a thinking sound
    text = text.replace("think", "uhhh... think")  # Adds 'thinking' sounds
    return text.strip()

# Function to generate audio
def generate_audio(text: str, output_path: str):
    """Generate speech from text using OuteTTS model and save as a .wav file."""
    try:
        gen_cfg = outetts.GenerationConfig(
            text=text,
            temperature=0.4,
            repetition_penalty=1.1,
            max_length=4096,
            speaker=speaker,
        )
        output = interface.generate(config=gen_cfg)
        output.save(output_path)
        print(f"Audio generated successfully at {output_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

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
        
        if page_number < 1 or page_number > len(reader.pages):
            raise HTTPException(status_code=400, detail="Invalid page number")
        
        page_text = reader.pages[page_number - 1].extract_text()
        if not page_text.strip():
            raise HTTPException(status_code=400, detail="No readable text on the page")
        
        cleaned_text = clean_text(page_text)
        audio_path = os.path.join(UPLOAD_DIR, f"page_{page_number}.wav")
        
        # Generate audio using OuteTTS
        generate_audio(cleaned_text, audio_path)
        
        return FileResponse(audio_path, media_type="audio/wav", filename=f"page_{page_number}.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
