from django import forms
from .models import Resume
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ResumeForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Add notes about this resume version or target position...',
            'class': 'form-control',
            'style': 'resize: vertical; min-height: 80px;'
        }),
        required=False,
        help_text='Add notes about this resume version or target position (optional).'
    )

    class Meta:
        model = Resume
        fields = ['title', 'description', 'document']
        labels = {
            'title': 'Resume Name',
            'description': 'Description',
            'document': 'Resume File',
        }
        help_texts = {
            'title': 'Give your resume a name to help you identify it (e.g., "Google SWE Resume").',
            'document': 'Upload your resume file (PDF or DOCX, max 5MB).',
        }

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # 1. File size validation (e.g., 5MB max)
            max_size = 5 * 1024 * 1024  # 5 MB in bytes
            if hasattr(document, 'size') and document.size > max_size:
                raise forms.ValidationError("File size must be under 5MB.")

            # 2. File type validation (only for new uploads)
            if hasattr(document, 'content_type'):
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
