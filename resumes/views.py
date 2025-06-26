from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Resume
from .forms import ResumeForm, RegisterForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from .utils import extract_text_from_resume, analyze_resume_with_gemini
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ResumeAnalysisSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Create your views here.


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            # Extract text from the uploaded file
            resume.text_content = extract_text_from_resume(resume.document)
            # Analyze with Gemini and store feedback
            ai_feedback = analyze_resume_with_gemini(resume.text_content)
            resume.ai_feedback = ai_feedback
            resume.save()
            if 'error' in ai_feedback:
                messages.warning(request, "Resume uploaded, but AI feedback could not be generated: {}".format(
                    ai_feedback.get('error')))
            else:
                messages.success(
                    request, "Resume uploaded and analyzed successfully!")
            return redirect('resume_list')
        else:
            messages.error(request, "There was a problem with your upload.")
    else:
        form = ResumeForm()
    return render(request, 'resumes/upload_resume.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('resume_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after successful registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f"Welcome to Resumely, {username}! Your account has been created successfully.")
                return redirect('resume_list')
            else:
                messages.error(
                    request, "Account created but automatic login failed. Please log in manually.")
                return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'resumes/register.html', {'form': form})


@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    # Define the sections for AI feedback display
    sections = ['summary', 'work_experience', 'education', 'skills']
    return render(request, 'resumes/resume_detail.html', {
        'resume': resume,
        'sections': sections
    })


@login_required
def edit_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume updated successfully!")
            return redirect('resume_detail', pk=resume.pk)
        else:
            messages.error(
                request, "There was a problem updating your resume.")
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'resumes/edit_resume.html', {'form': form, 'resume': resume})


@login_required
def delete_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        # Delete the file from storage
        if resume.document:
            resume.document.delete(save=False)
        # Delete the database record
        resume.delete()
        messages.success(request, "Resume deleted successfully!")
        return redirect('resume_list')
    return render(request, 'resumes/delete_resume.html', {'resume': resume})


@login_required
def profile(request):
    return render(request, 'resumes/profile.html')


class ResumeAnalysisAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # Support file uploads, form data, and JSON
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    """
    API endpoint for analyzing resume text with Gemini AI.
    Accepts POST with resume_text or resume_file, returns structured ai_feedback.
    """

    def post(self, request, *args, **kwargs):
        serializer = ResumeAnalysisSerializer(
            data=request.data, files=request.FILES)
        if serializer.is_valid():
            # Prefer file if provided, else use text
            resume_file = serializer.validated_data.get('resume_file')
            resume_text = serializer.validated_data.get('resume_text')
            if resume_file:
                try:
                    # Use the utility to extract text from the uploaded file
                    resume_text = extract_text_from_resume(resume_file)
                except Exception as e:
                    return Response({'error': f'Failed to extract text from file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            # If only text is provided, use as is
            ai_feedback = analyze_resume_with_gemini(resume_text)
            return Response({'ai_feedback': ai_feedback}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
