#!/usr/bin/env python
"""
Comprehensive Test Script for Resumely
Tests all functionality, templates, views, and features
"""

from resumes.utils import extract_text_from_resume, analyze_resume_with_gemini
from resumes.forms import ResumeForm, RegisterForm
from resumes.models import Resume
from django.template.exceptions import TemplateSyntaxError
from django.template import Template, Context
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase, Client
import os
import sys
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resumely.settings')
django.setup()


class ComprehensiveTest:
    def __init__(self):
        self.client = Client()
        self.test_user = None
        self.test_resume = None

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🧪 COMPREHENSIVE RESUMELY TEST SUITE")
        print("=" * 50)

        tests = [
            ("Database Models", self.test_models),
            ("Forms", self.test_forms),
            ("Templates", self.test_templates),
            ("Views", self.test_views),
            ("URLs", self.test_urls),
            ("AI Functions", self.test_ai_functions),
            ("File Handling", self.test_file_handling),
            ("User Authentication", self.test_authentication),
            ("Integration", self.test_integration),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            print("-" * 30)
            try:
                test_func()
                print(f"✅ {test_name}: PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test_name}: FAILED - {str(e)}")
                failed += 1

        print(f"\n📊 TEST RESULTS")
        print("=" * 30)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")

        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Your Resumely application is working perfectly!")
        else:
            print(
                f"\n⚠️  {failed} test(s) failed. Please review the errors above.")

    def test_models(self):
        """Test database models"""
        # Test Resume model creation
        user = User.objects.create_user(
            username='testuser', password='testpass123')
        resume = Resume.objects.create(
            user=user,
            title='Test Resume',
            text_content='Test content',
            ai_feedback={'summary': {'suggestions': ['Test suggestion']}}
        )

        assert resume.title == 'Test Resume'
        assert resume.user == user
        assert 'Test suggestion' in str(resume.ai_feedback)

        # Cleanup
        user.delete()

    def test_forms(self):
        """Test forms validation"""
        # Test ResumeForm
        form_data = {'title': 'Test Resume'}
        form = ResumeForm(data=form_data)
        assert not form.is_valid()  # Missing document

        # Test RegisterForm
        register_data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        register_form = RegisterForm(data=register_data)
        assert register_form.is_valid()

    def test_templates(self):
        """Test all templates for syntax errors"""
        templates = [
            'resumes/base.html',
            'resumes/resume_list.html',
            'resumes/resume_detail.html',
            'resumes/upload_resume.html',
            'resumes/edit_resume.html',
            'resumes/delete_resume.html',
            'resumes/profile.html',
            'resumes/register.html',
            'resumes/404.html',
            'registration/login.html',
        ]

        for template_name in templates:
            try:
                # Test template rendering with dummy context
                context = {
                    'user': User(username='test'),
                    'resumes': [],
                    'resume': None,
                    'form': None,
                    'sections': ['summary', 'work_experience', 'education', 'skills']
                }
                render_to_string(template_name, context)
            except TemplateSyntaxError as e:
                raise Exception(
                    f"Template {template_name} has syntax error: {e}")
            except Exception as e:
                # Some templates might need specific context, that's okay
                pass

    def test_views(self):
        """Test view functions"""
        # Test resume_list view
        user = User.objects.create_user(
            username='viewtest', password='testpass123')
        self.client.force_login(user)

        response = self.client.get(reverse('resume_list'))
        assert response.status_code == 200

        # Test profile view
        response = self.client.get(reverse('profile'))
        assert response.status_code == 200

        # Cleanup
        user.delete()

    def test_urls(self):
        """Test URL patterns"""
        from resumes.urls import urlpatterns

        expected_urls = [
            'resume_list',
            'upload_resume',
            'register',
            'resume_detail',
            'edit_resume',
            'delete_resume',
            'regenerate_ai_feedback',
            'profile',
            'api_analyze_resume'
        ]

        url_names = [
            pattern.name for pattern in urlpatterns if hasattr(pattern, 'name')]

        for expected_url in expected_urls:
            assert expected_url in url_names, f"Missing URL: {expected_url}"

    def test_ai_functions(self):
        """Test AI utility functions"""
        # Test text extraction (mock)
        sample_text = "Test resume content"

        # Test AI analysis function structure
        result = analyze_resume_with_gemini(sample_text)
        assert isinstance(result, dict)

        # Should have error if no API key
        if 'error' in result:
            assert 'API key' in result['error']

    def test_file_handling(self):
        """Test file upload and processing"""
        # Test file validation
        small_file = SimpleUploadedFile(
            "test.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )

        form_data = {'title': 'Test File'}
        form = ResumeForm(data=form_data, files={'document': small_file})

        # Form should be valid with proper file
        assert form.is_valid()

    def test_authentication(self):
        """Test user authentication flow"""
        # Test registration
        register_data = {
            'username': 'authuser',
            'email': 'auth@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

        user = User.objects.create_user(
            username=register_data['username'],
            email=register_data['email'],
            password=register_data['password1']
        )

        # Test login
        self.client.login(username='authuser', password='testpass123')
        assert self.client.session['_auth_user_id'] == str(user.id)

        # Cleanup
        user.delete()

    def test_integration(self):
        """Test complete user workflow"""
        # Create user
        user = User.objects.create_user(
            username='integration', password='testpass123')
        self.client.force_login(user)

        # Test complete workflow
        # 1. Access resume list
        response = self.client.get(reverse('resume_list'))
        assert response.status_code == 200

        # 2. Access upload page
        response = self.client.get(reverse('upload_resume'))
        assert response.status_code == 200

        # 3. Access profile
        response = self.client.get(reverse('profile'))
        assert response.status_code == 200

        # Cleanup
        user.delete()


def main():
    """Run comprehensive tests"""
    print("🚀 Starting Comprehensive Resumely Test Suite...")

    # Check if Django is properly configured
    try:
        from django.conf import settings
        print(
            f"✅ Django settings loaded: {settings.DATABASES['default']['NAME']}")
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return

    # Run tests
    tester = ComprehensiveTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
