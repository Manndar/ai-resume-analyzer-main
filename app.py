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

def extract_keywords(text, top_n=10):
    """Extract keywords from a text using simple word frequency."""
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = set([
        "the", "and", "to", "of", "in", "a", "for", "with", "on", "is", "as", "by", "an", "be", "are", "at", "from"
    ])
    freq = {}
    for word in words:
        if word not in stopwords and len(word) > 2:
            freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq, key=freq.get, reverse=True)
    return sorted_words[:top_n]

def calculate_resume_score(resume_text, job_description):
    """Calculate a simple score based on keyword overlap."""
    if not job_description:
        return None
    resume_keywords = set(extract_keywords(resume_text, 20))
    jd_keywords = set(extract_keywords(job_description, 20))
    if not jd_keywords:
        return 0
    overlap = resume_keywords & jd_keywords
    score = int((len(overlap) / len(jd_keywords)) * 100)
    return score, overlap, jd_keywords - resume_keywords

def get_text_download_link(text, filename="analysis.txt"):
    """Generate a download link for the analysis text."""
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Feedback Report</a>'
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


def analyze_resume_with_gemini(resume_text, job_description=None):
    """Analyze resume text using Gemini AI, optionally with a job description."""
    if not resume_text:
        return {"error": "Resume text is required for analysis."} 
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    base_prompt = f"""
    You are an experienced HR with Technical Experience in the field of any one job role from Data Science, Data Analyst, DevOPS, Machine Learning Engineer, Prompt Engineer, AI Engineer, Full Stack Web Development, Big Data Engineering, Marketing Analyst, Human Resource Manager, Software Developer your task is to review the provided resume.
    Please share your professional evaluation on whether the candidate's profile aligns with the role.ALso mention Skills he already have and siggest some skills to imorve his resume , alos suggest some course he might take to improve the skills.Highlight the strengths and weaknesses in short.
    Try to provide evaluation in short and concise manner, with a focus on actionable feedback.
    Resume:
    {resume_text}
    """
    if job_description:
        base_prompt += f"""
        Additionally, compare this resume to the following job description:
        Job Description:
        {job_description}
        Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
        """
    response = model.generate_content(base_prompt)
    analysis = response.text.strip()
    return analysis


def main():
    configure_app()
    st.set_page_config(page_title="Resume Analyzer", layout="wide")
    st.title("AI Resume Analyzer")
    st.write("Analyze your resume and match it with job descriptions using Google Gemini AI.")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    with col2:
        job_description = st.text_area("Enter Job Description:", placeholder="Paste the job description here...")

    if uploaded_file is not None:
        st.success("Resume uploaded successfully!")
    else:
        st.warning("Please upload a resume in PDF format.")

    st.markdown("<div style= 'padding-top: 10px;'></div>", unsafe_allow_html=True)
    if uploaded_file:
        with open("uploaded_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        resume_text = extract_text_from_pdf("uploaded_resume.pdf")
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing resume..."):
                try:
                    analysis = analyze_resume_with_gemini(resume_text, job_description)
                    st.success("Analysis complete!")
                    
                    # 1. Resume Scoring & Keyword Highlighting
                    score, present, missing = calculate_resume_score(resume_text, job_description)
                    st.markdown(f"### Resume Score: **{score}/100**")
                    st.markdown("#### Keyword Match")
                    st.markdown(f"**Present:** {', '.join(present) if present else 'None'}")
                    st.markdown(f"**Missing:** {', '.join(missing) if missing else 'None'}")

                    # 3. Highlight keywords in analysis
                    highlighted_analysis = highlight_keywords(analysis, present)
                    st.markdown(highlighted_analysis, unsafe_allow_html=True)

                    # 2. Downloadable Feedback Report
                    st.markdown(get_text_download_link(analysis), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    st.markdown("---")
    st.markdown("""<p style= 'text-align: center;' >Powered by <b>Streamlit</b> and <b>Google Gemini AI</b> | Developed by <a href=\"https://www.linkedin.com/in/mandar-lokhande/\"  target=\"_blank\" style='text-decoration: none; color: #FFFFFF'><b>Mandar Lokhande</b></a></p>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
