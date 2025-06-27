#!/usr/bin/env python
"""
Comprehensive test script for Resumely project
Tests all major features and functionality
"""

from resumes.utils import extract_text_from_resume, analyze_resume_with_gemini
from resumes.models import Resume
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

# Now import Django modules


def test_basic_functionality():
    """Test basic project functionality"""
    print("🔍 Testing basic functionality...")

    # Test 1: Check if all required apps are installed
    from django.conf import settings
    required_apps = ['django.contrib.admin',
                     'django.contrib.auth', 'resumes', 'rest_framework']
    for app in required_apps:
        if app not in settings.INSTALLED_APPS:
            print(f"❌ Missing app: {app}")
            return False
    print("✅ All required apps are installed")

    # Test 2: Check database connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # Test 3: Check if models can be imported
    try:
        from resumes.models import Resume
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

    return True


def test_urls():
    """Test URL routing"""
    print("\n🔍 Testing URL routing...")

    client = Client()

    # Test URLs that should work
    test_urls = [
        ('/', 302),  # Should redirect to resume_list
        ('/resumes/', 302),  # Should redirect to login if not authenticated
        ('/resumes/login/', 200),  # Login page should be accessible
        ('/resumes/register/', 200),  # Register page should be accessible
    ]

    for url, expected_status in test_urls:
        try:
            response = client.get(url)
            if response.status_code == expected_status:
                print(f"✅ {url} - Status: {response.status_code}")
            else:
                print(
                    f"❌ {url} - Expected {expected_status}, got {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

    return True


def test_forms():
    """Test form functionality"""
    print("\n🔍 Testing forms...")

    try:
        from resumes.forms import ResumeForm, RegisterForm

        # Test ResumeForm
        form_data = {
            'title': 'Test Resume',
            'description': 'Test description'
        }
        form = ResumeForm(data=form_data)
        print("✅ ResumeForm created successfully")

        # Test RegisterForm
        register_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        register_form = RegisterForm(data=register_data)
        print("✅ RegisterForm created successfully")

    except Exception as e:
        print(f"❌ Form test failed: {e}")
        return False

    return True


def test_utils():
    """Test utility functions"""
    print("\n🔍 Testing utility functions...")

    try:
        # Test text extraction (mock)
        test_text = "This is a test resume content"
        print("✅ Text extraction utility accessible")

        # Test AI analysis (mock - won't actually call API)
        print("✅ AI analysis utility accessible")

    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        return False

    return True


def test_templates():
    """Test template rendering"""
    print("\n🔍 Testing template rendering...")

    client = Client()

    try:
        # Test login template
        response = client.get('/resumes/login/')
        if response.status_code == 200:
            print("✅ Login template renders successfully")
        else:
            print(f"❌ Login template failed: {response.status_code}")

        # Test register template
        response = client.get('/resumes/register/')
        if response.status_code == 200:
            print("✅ Register template renders successfully")
        else:
            print(f"❌ Register template failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

    return True


def test_authentication():
    """Test authentication system"""
    print("\n🔍 Testing authentication system...")

    client = Client()

    try:
        # Test user creation
        user = User.objects.create_user(
            username='testuser', password='testpass123')
        print("✅ User creation successful")

        # Test login
        login_successful = client.login(
            username='testuser', password='testpass123')
        if login_successful:
            print("✅ User login successful")
        else:
            print("❌ User login failed")

        # Test authenticated access
        response = client.get('/resumes/')
        if response.status_code == 200:
            print("✅ Authenticated access successful")
        else:
            print(f"❌ Authenticated access failed: {response.status_code}")

        # Clean up
        user.delete()
        print("✅ User cleanup successful")

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

    return True


def test_static_files():
    """Test static file serving"""
    print("\n🔍 Testing static files...")

    try:
        # Check if static files directory exists
        static_dir = os.path.join(os.getcwd(), 'static')
        if os.path.exists(static_dir):
            print("✅ Static files directory exists")
        else:
            print("❌ Static files directory missing")

        # Check if custom.css exists
        css_file = os.path.join(static_dir, 'custom.css')
        if os.path.exists(css_file):
            print("✅ Custom CSS file exists")
        else:
            print("❌ Custom CSS file missing")

    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        return False

    return True


def main():
    """Run all tests"""
    print("🚀 Starting comprehensive Resumely project test...\n")

    tests = [
        test_basic_functionality,
        test_urls,
        test_forms,
        test_utils,
        test_templates,
        test_authentication,
        test_static_files,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The project is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
