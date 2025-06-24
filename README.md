# Resumely

**Resumely** is an AI-powered resume checker and career coach web application built with Django and PostgreSQL.  
It allows users to securely upload, manage, and analyze their resumes, with plans for advanced AI feedback and job tracking features.

---

## 🚀 Features

- **User Registration & Authentication:**  
  Secure sign-up, login, logout, and user profile page.
- **Resume Management:**  
  - Upload, view, edit, and delete resumes (PDF, DOCX, etc.)
  - Each user can manage their own private resumes.
- **Resume Detail View:**  
  See all information about a specific resume, with download and management options.
- **Clean, Modular Django Codebase:**  
  Follows best practices for scalability and maintainability.
- **Ready for AI Integration:**  
  The foundation is set for adding AI-powered resume analysis and career coaching.

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **Frontend:** Django Templates (Bootstrap/Tailwind planned)
- **Version Control:** Git & GitHub

---

## 📦 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/resumely.git
   cd resumely
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your database in `settings.py`**  
   (Set up PostgreSQL and update credentials as needed.)

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Visit:**  
   - `http://localhost:8000/resumes/` to manage resumes  
   - `http://localhost:8000/accounts/register/` to sign up

---

## 📚 Roadmap

- [x] User authentication and registration
- [x] Resume upload, list, detail, edit, delete (CRUD)
- [x] User profile page
- [ ] AI-powered resume analysis
- [ ] Job application tracker
- [ ] Beautiful, modern UI/UX (Bootstrap/Tailwind)
- [ ] RESTful API (Django REST Framework)
- [ ] Deployment to cloud

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
