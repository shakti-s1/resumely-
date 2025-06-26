import os
from docx import Document
from PyPDF2 import PdfReader
import json
import google.generativeai as genai


def extract_text_from_resume(file_field):
    """Extract text content from uploaded resume file (PDF or DOCX)."""
    ext = os.path.splitext(file_field.name)[1].lower()
    if ext == ".pdf":
        try:
            reader = PdfReader(file_field)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    elif ext == ".docx":
        try:
            doc = Document(file_field)
            text = "\n".join(
                [para.text for para in doc.paragraphs if para.text.strip()])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    else:
        raise ValueError(
            "Unsupported file type. Please upload PDF or DOCX files only.")


def analyze_resume_with_gemini(resume_text):
    """
    Sends resume text to Gemini LLM for structured analysis and returns JSON feedback.
    Args:
        resume_text (str): The extracted text from the resume.
    Returns:
        dict: Parsed JSON feedback from Gemini, or error info.
    """
    # Validate input
    if not resume_text or not resume_text.strip():
        return {'error': 'No resume text provided for analysis.'}

    # Get Gemini API key from environment variable
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        return {'error': 'Gemini API key not set. Please set GEMINI_API_KEY environment variable.'}

    # Configure Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        return {'error': f'Failed to configure Gemini API: {str(e)}'}

    # Build a more detailed prompt for better analysis
    prompt = (
        "You are an expert resume reviewer and career coach with 10+ years of experience. "
        "Analyze the following resume text and provide comprehensive feedback. "
        "For each section (summary, work_experience, education, skills), provide feedback as a JSON object with this exact structure:\n"
        "{\n"
        "  'summary': {\n"
        "    'suggestions': ['specific improvement suggestions'],\n"
        "    'rewrites': [{'original': 'original text', 'improved': 'improved version'}],\n"
        "    'ats_check': ['ATS compatibility checks']\n"
        "  },\n"
        "  'work_experience': {\n"
        "    'suggestions': ['specific improvement suggestions'],\n"
        "    'rewrites': [{'original': 'original bullet', 'improved': 'improved bullet'}],\n"
        "    'ats_check': ['ATS compatibility checks']\n"
        "  },\n"
        "  'education': {\n"
        "    'suggestions': ['specific improvement suggestions'],\n"
        "    'rewrites': [{'original': 'original text', 'improved': 'improved version'}],\n"
        "    'ats_check': ['ATS compatibility checks']\n"
        "  },\n"
        "  'skills': {\n"
        "    'suggestions': ['specific improvement suggestions'],\n"
        "    'rewrites': [{'original': 'original text', 'improved': 'improved version'}],\n"
        "    'ats_check': ['ATS compatibility checks']\n"
        "  }\n"
        "}\n\n"
        "Guidelines:\n"
        "- Provide actionable, specific feedback\n"
        "- Focus on ATS optimization and modern resume best practices\n"
        "- If a section is missing or unclear, provide suggestions for what to add\n"
        "- Keep suggestions concise but helpful\n"
        "- Respond ONLY with valid JSON, no additional text\n\n"
        # Limit text length to avoid token limits
        f"Resume Text:\n{resume_text[:8000]}"
    )

    try:
        # Use Gemini's 2.5 Flash model for best performance
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean the response text to ensure it's valid JSON
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        feedback = json.loads(response_text)

        # Validate the structure
        expected_sections = ['summary',
                             'work_experience', 'education', 'skills']
        for section in expected_sections:
            if section not in feedback:
                feedback[section] = {
                    'suggestions': [],
                    'rewrites': [],
                    'ats_check': []
                }
            elif not isinstance(feedback[section], dict):
                feedback[section] = {
                    'suggestions': [],
                    'rewrites': [],
                    'ats_check': []
                }
            else:
                # Ensure all required keys exist
                for key in ['suggestions', 'rewrites', 'ats_check']:
                    if key not in feedback[section]:
                        feedback[section][key] = []
                    elif not isinstance(feedback[section][key], list):
                        feedback[section][key] = []

        return feedback

    except json.JSONDecodeError as e:
        return {
            'error': 'Failed to parse AI response as JSON. The AI may have returned invalid format.',
            'raw_response': response_text,
            'json_error': str(e)
        }
    except Exception as e:
        return {'error': f'AI analysis failed: {str(e)}'}
