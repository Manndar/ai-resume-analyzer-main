import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import io
import re
import base64
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

def get_text_download_link(text, filename=None):
    """Generate a download link for the text content."""
    from datetime import datetime
    
    if filename is None:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_analysis_{timestamp}.txt"
    
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">Download Feedback Report</a>'
    return href

def highlight_keywords(text, keywords):
    """Highlight keywords in the text."""
    for kw in keywords:
        text = re.sub(f"\\b({re.escape(kw)})\\b", r"<mark>\1</mark>", text, flags=re.IGNORECASE)
    return text

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

# Add this function at the top level with other functions
def clear_job_description():
    """Callback function to clear job description"""
    st.session_state.job_description = ""
    st.session_state.text_area = ""
    
def analyze_resume_with_gemini(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."} 
    
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

    response = model.generate_content(base_prompt)
    analysis = response.text.strip()
    return analysis


def main():
    configure_app()
    st.set_page_config(page_title="Resume Analyzer", layout="wide")
    st.title("AI Resume Analyzer")
    st.write("Analyze your resume and match it with job descriptions using Google Gemini AI.")

   # Initialize session state for job description if it doesn't exist
    if 'job_description' not in st.session_state:
        st.session_state.job_description = ""
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    with col2:
        job_description = st.text_area(
            "Enter Job Description:",
            key="text_area",  # Add a key for the text area
            value=st.session_state.job_description,
            placeholder="Paste the job description here..."
        )
        st.button("Clear", on_click=clear_job_description)  # Use the callback function
    
    
    # Update session state with current text area value
    st.session_state.job_description = job_description
    
    if uploaded_file is not None:
        st.success("Resume uploaded successfully!")
    else:
        st.warning("Please upload a resume in PDF format.")

    st.markdown("<div style= 'padding-top: 10px;'></div>", unsafe_allow_html=True)
    if uploaded_file:
        fileNameWithoutExt = uploaded_file.name.split(".")[0]
        with open("uploaded_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        resume_text = extract_text_from_pdf("uploaded_resume.pdf")
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing resume..."):
                try:
                    analysis = analyze_resume_with_gemini(resume_text, job_description)
                    st.success("Analysis complete!")               
                    st.markdown(analysis, unsafe_allow_html=True)

                    # 2. Downloadable Feedback Report
                    st.markdown(get_text_download_link(analysis, fileNameWithoutExt), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    st.markdown("---")
    st.markdown("""<p style= 'text-align: center;' >Powered by <b>Streamlit</b> and <b>Google Gemini AI</b> | Developed by <a href=\"https://www.linkedin.com/in/mandar-lokhande/\"  target=\"_blank\" style='text-decoration: none; color: #FFFFFF'><b>Mandar Lokhande</b></a></p>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
