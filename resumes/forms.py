from django import forms
from .models import Resume
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'document']

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # 1. File size validation (e.g., 5MB max)
            max_size = 5 * 1024 * 1024  # 5 MB in bytes
            if document.size > max_size:
                raise forms.ValidationError("File size must be under 5MB.")

            # 2. File type validation
            allowed_types = [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if document.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Only PDF and DOCX files are allowed.")
        return document


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
