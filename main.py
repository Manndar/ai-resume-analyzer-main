from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import uvicorn
from typing import Optional
import tempfile

app = FastAPI(title="AI Resume Analyzer API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def configure_app():
    """Load environment variables and configure Gemini AI."""
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file, using OCR as fallback."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")
    
    # Fallback to OCR
    print("Falling back to OCR for image-based PDF.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")
    return text.strip()

def analyze_resume_with_gemini(resume_text: str, job_description: Optional[str] = None):
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required for analysis.")
    
    model = genai.GenerativeModel("gemini-1.5-flash")

    base_prompt = f"""
    You are an experienced HR professional with deep technical understanding in fields like Data Science, DevOps, AI, and Software Development.

    Please analyze the following resume. Provide:
    1. A resume-job match **score out of 100**
    2. Key **skills present** in the resume
    3. Key **skills missing**
    4. **Strengths and weaknesses** in a few bullet points
    5. Final review of the resume.   

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""

        Compare the resume against this job description:
        {job_description}

        Be specific and concise. Use short, actionable feedback wherever possible.
        """

    try:
        response = model.generate_content(base_prompt)
        analysis = response.text.strip()
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Initialize the app on startup
@app.on_event("startup")
async def startup_event():
    configure_app()

@app.post("/analyze-resume/")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """
    Analyze a resume and optionally compare it with a job description.
    
    Parameters:
    - resume: PDF file containing the resume
    - job_description: Optional job description text to compare against
    
    Returns:
    - JSON object containing the analysis results
    """
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            contents = await resume.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(temp_file_path)
        
        # Remove temporary file
        os.unlink(temp_file_path)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF")
        
        # Analyze resume
        analysis_result = analyze_resume_with_gemini(resume_text, job_description)
        return JSONResponse(content=analysis_result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": "AI Resume Analyzer API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
