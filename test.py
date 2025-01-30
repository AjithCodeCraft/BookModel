import fitz  # PyMuPDF for extracting text from PDFs
import tkinter as tk
from tkinter import filedialog
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()

# Global variables
pdf_path = ""
doc = None
current_page = 0

# Function to open PDF file
def open_pdf():
    global pdf_path, doc, current_page
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if pdf_path:
        doc = fitz.open(pdf_path)
        current_page = 0
        read_page()

# Function to extract text from the current page
def extract_text(page_num):
    if doc and 0 <= page_num < len(doc):
        return doc[page_num].get_text("text")
    return ""

# Function to convert text to speech using PicoTTS (via pyttsx3)
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()

# Function to read the current page
def read_page():
    global current_page
    text = extract_text(current_page)
    if text.strip():
        text_display.config(state=tk.NORMAL)
        text_display.delete("1.0", tk.END)
        text_display.insert(tk.END, text)
        text_display.config(state=tk.DISABLED)
        text_to_speech(text)

# Function to go to the next page
def next_page():
    global current_page
    if doc and current_page < len(doc) - 1:
        current_page += 1
        read_page()

# Function to go to the previous page
def prev_page():
    global current_page
    if doc and current_page > 0:
        current_page -= 1
        read_page()

# GUI Setup
root = tk.Tk()
root.title("Real-Time Text-to-Speech Reader")
root.geometry("600x400")

# Buttons
btn_open = tk.Button(root, text="Open PDF", command=open_pdf)
btn_open.pack()
btn_prev = tk.Button(root, text="Previous Page", command=prev_page)
btn_prev.pack()
btn_next = tk.Button(root, text="Next Page", command=next_page)
btn_next.pack()

# Text display
text_display = tk.Text(root, height=10, wrap=tk.WORD)
text_display.pack()
text_display.config(state=tk.DISABLED)

# Run the GUI
root.mainloop() 
