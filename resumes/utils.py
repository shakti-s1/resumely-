import os
from docx import Document
from PyPDF2 import PdfReader
import json
import google.generativeai as genai


def extract_text_from_resume(file_field):
    ext = os.path.splitext(file_field.name)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_field)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif ext == ".docx":
        doc = Document(file_field)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type")


def analyze_resume_with_gemini(resume_text):
    """
    Sends resume text to Gemini LLM for structured analysis and returns JSON feedback.
    Args:
        resume_text (str): The extracted text from the resume.
    Returns:
        dict: Parsed JSON feedback from Gemini, or error info.
    """
    # Get Gemini API key from environment variable
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        return {'error': 'Gemini API key not set in environment variable GEMINI_API_KEY.'}

    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)

    # Build the prompt for structured JSON feedback
    prompt = (
        "You are an expert resume reviewer and career coach. "
        "Analyze the following resume text. For each section (Summary, Work Experience, Education, Skills), "
        "provide feedback as a JSON object with the following structure: "
        "{ 'summary': { 'suggestions': [..], 'rewrites': [..], 'ats_check': [..] }, "
        "  'work_experience': { 'suggestions': [..], 'rewrites': [..], 'ats_check': [..] }, "
        "  'education': { ... }, 'skills': { ... } } "
        "Each array should contain bullet-level feedback. "
        "If a section is missing, return an empty array for that section. "
        "Respond ONLY with the JSON object, no extra text.\n\n"
        f"Resume Text:\n{resume_text}"
    )

    try:
        # Use Gemini's 2.5 Flash model for best performance
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        feedback = json.loads(response_text)
        return feedback
    except json.JSONDecodeError:
        return {'error': 'Failed to parse Gemini response as JSON.', 'raw_response': response_text}
    except Exception as e:
        return {'error': str(e)}
