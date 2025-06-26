# Resumely

**Resumely** is an AI-powered resume checker and career coach web application built with Django and PostgreSQL.  
It allows users to securely upload, manage, and analyze their resumes with advanced AI feedback and career insights.

---

## 🚀 Features

- **User Registration & Authentication:**  
  Secure sign-up, login, logout, and user profile page.
- **Resume Management:**  
  - Upload, view, edit, and delete resumes (PDF, DOCX, etc.)
  - Each user can manage their own private resumes.
- **AI-Powered Resume Analysis:**
  - Comprehensive feedback on Summary, Work Experience, Education, and Skills sections
  - Actionable suggestions for improvement
  - ATS (Applicant Tracking System) optimization checks
  - Bullet point rewrites and enhancements
  - Regenerate AI feedback for updated analysis
- **Resume Detail View:**  
  See all information about a specific resume, with download and management options.
- **Clean, Modular Django Codebase:**  
  Follows best practices for scalability and maintainability.

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **AI:** Google Gemini API for resume analysis
- **Frontend:** Django Templates with Bootstrap
- **File Processing:** PyPDF2, python-docx
- **Version Control:** Git & GitHub

---

## 📦 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/resumely.git
   cd resumely
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ```
   
   **To get a Gemini API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key to your `.env` file

5. **Configure your database in `settings.py`**  
   (Set up PostgreSQL and update credentials as needed.)

6. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

9. **Visit:**  
   - `http://localhost:8000/resumes/` to manage resumes  
   - `http://localhost:8000/accounts/register/` to sign up

---

## 🤖 AI Features

The AI analysis provides comprehensive feedback on:

- **Summary Section:** Suggestions for compelling professional summaries
- **Work Experience:** Bullet point improvements and achievement-focused rewrites
- **Education:** Formatting and content suggestions
- **Skills:** Optimization for ATS systems and relevance

Each section includes:
- 💡 **Suggestions:** Specific improvement recommendations
- ✍️ **Rewrites:** Enhanced versions of existing content
- 🛡️ **ATS Check:** Compatibility with Applicant Tracking Systems

---

## 📚 Roadmap

- [x] User authentication and registration
- [x] Resume upload, list, detail, edit, delete (CRUD)
- [x] User profile page
- [x] AI-powered resume analysis
- [x] File validation and cleanup
- [ ] Job application tracker
- [ ] Resume templates and customization
- [ ] Export functionality
- [ ] Advanced analytics and insights

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

[MIT](LICENSE)

---

## 🙋‍♂️ Author

- **Shakti** ([GitHub](https://github.com/shakti-s1))

---

*Built with ❤️ using Django.*
