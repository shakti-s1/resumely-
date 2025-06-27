import os
from docx import Document
from PyPDF2 import PdfReader
import json
import google.generativeai as genai
from decouple import config


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

    # Get Gemini API key from environment variable using python-decouple
    GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        return {'error': 'Gemini API key not set. Please set GEMINI_API_KEY environment variable.'}

    # Configure Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        return {'error': f'Failed to configure Gemini API: {str(e)}'}

    # Enhanced prompt for comprehensive resume analysis
    prompt = (
        "You are an expert resume reviewer and career coach with 10+ years of experience. "
        "Analyze the following resume text and provide comprehensive, actionable feedback. "
        "For each section, provide detailed analysis and specific improvements.\n\n"
        "Return ONLY valid JSON in this exact structure:\n"
        "{\n"
        "  'summary': {\n"
        "    'original_text': 'extracted summary text or empty string',\n"
        "    'feedback': 'detailed analysis of what works and what needs improvement',\n"
        "    'suggestions': ['specific, actionable improvement suggestions'],\n"
        "    'rewrites': [\n"
        "      {\n"
        "        'original': 'original text if found',\n"
        "        'improved': 'completely rewritten, ATS-optimized version',\n"
        "        'explanation': 'brief explanation of improvements made'\n"
        "      }\n"
        "    ],\n"
        "    'ats_check': ['ATS compatibility checks and recommendations']\n"
        "  },\n"
        "  'work_experience': {\n"
        "    'original_text': 'extracted work experience text or empty string',\n"
        "    'feedback': 'detailed analysis of work experience section',\n"
        "    'suggestions': ['specific improvement suggestions for job descriptions'],\n"
        "    'rewrites': [\n"
        "      {\n"
        "        'original': 'original bullet point or description',\n"
        "        'improved': 'quantified, action-oriented improved version',\n"
        "        'explanation': 'explanation of improvements (quantification, action verbs, etc.)'\n"
        "      }\n"
        "    ],\n"
        "    'ats_check': ['ATS compatibility checks for work experience']\n"
        "  },\n"
        "  'education': {\n"
        "    'original_text': 'extracted education text or empty string',\n"
        "    'feedback': 'analysis of education section',\n"
        "    'suggestions': ['suggestions for education section improvement'],\n"
        "    'rewrites': [\n"
        "      {\n"
        "        'original': 'original education text',\n"
        "        'improved': 'improved education section format',\n"
        "        'explanation': 'explanation of improvements'\n"
        "      }\n"
        "    ],\n"
        "    'ats_check': ['ATS compatibility checks for education']\n"
        "  },\n"
        "  'skills': {\n"
        "    'original_text': 'extracted skills text or empty string',\n"
        "    'feedback': 'analysis of skills section',\n"
        "    'suggestions': ['suggestions for skills section improvement'],\n"
        "    'rewrites': [\n"
        "      {\n"
        "        'original': 'original skills list',\n"
        "        'improved': 'organized, relevant skills list',\n"
        "        'explanation': 'explanation of skills organization and relevance'\n"
        "      }\n"
        "    ],\n"
        "    'ats_check': ['ATS compatibility checks for skills']\n"
        "  },\n"
        "  'projects': {\n"
        "    'original_text': 'extracted projects text or empty string',\n"
        "    'feedback': 'analysis of projects section',\n"
        "    'suggestions': ['suggestions for projects section improvement'],\n"
        "    'rewrites': [\n"
        "      {\n"
        "        'original': 'original project description',\n"
        "        'improved': 'improved project description with impact',\n"
        "        'explanation': 'explanation of project improvements'\n"
        "      }\n"
        "    ],\n"
        "    'ats_check': ['ATS compatibility checks for projects']\n"
        "  }\n"
        "}\n\n"
        "Guidelines for analysis:\n"
        "1. Extract and identify the original text for each section\n"
        "2. Provide specific, actionable feedback\n"
        "3. Focus on ATS optimization and modern resume best practices\n"
        "4. Use quantifiable achievements and action verbs in rewrites\n"
        "5. If a section is missing, suggest what to add\n"
        "6. Keep suggestions concise but helpful\n"
        "7. Ensure all rewrites are ATS-friendly and impactful\n\n"
        "Resume Text:\n{resume_text[:8000]}"
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

        # Validate and ensure the structure
        expected_sections = ['summary', 'work_experience',
                             'education', 'skills', 'projects']
        for section in expected_sections:
            if section not in feedback:
                feedback[section] = {
                    'original_text': '',
                    'feedback': 'No content found for this section.',
                    'suggestions': [],
                    'rewrites': [],
                    'ats_check': []
                }
            elif not isinstance(feedback[section], dict):
                feedback[section] = {
                    'original_text': '',
                    'feedback': 'Invalid section format.',
                    'suggestions': [],
                    'rewrites': [],
                    'ats_check': []
                }
            else:
                # Ensure all required keys exist
                required_keys = ['original_text', 'feedback',
                                 'suggestions', 'rewrites', 'ats_check']
                for key in required_keys:
                    if key not in feedback[section]:
                        if key == 'original_text':
                            feedback[section][key] = ''
                        elif key == 'feedback':
                            feedback[section][key] = 'No feedback available for this section.'
                        else:
                            feedback[section][key] = []
                    elif key in ['suggestions', 'rewrites', 'ats_check'] and not isinstance(feedback[section][key], list):
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
