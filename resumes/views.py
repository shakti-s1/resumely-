from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
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
from datetime import datetime
from django.http import JsonResponse

# Create your views here.


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-created_at')

    # Calculate statistics for the enhanced template
    resumes_with_ai = resumes.filter(ai_feedback__isnull=False).exclude(
        ai_feedback__error__isnull=False)

    # Get resumes from this month
    from datetime import datetime, timedelta
    from django.utils import timezone
    this_month = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)
    recent_resumes = resumes.filter(created_at__gte=this_month)

    context = {
        'resumes': resumes,
        'resumes_with_ai': resumes_with_ai,
        'recent_resumes': recent_resumes,
    }

    return render(request, 'resumes/resume_list.html', context)


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resume = form.save(commit=False)
                resume.user = request.user

                # Extract text from the uploaded file
                try:
                    resume.text_content = extract_text_from_resume(
                        resume.document)
                    if not resume.text_content.strip():
                        messages.warning(
                            request, "Resume uploaded, but no text could be extracted. Please ensure your file contains readable text.")
                        resume.save()
                        return redirect('resume_detail', pk=resume.pk)
                except Exception as e:
                    messages.error(
                        request, f"Failed to extract text from resume: {str(e)}")
                    return render(request, 'resumes/upload_resume.html', {'form': form})

                # Analyze with Gemini and store feedback
                try:
                    ai_feedback = analyze_resume_with_gemini(
                        resume.text_content)
                    resume.ai_feedback = ai_feedback

                    if 'error' in ai_feedback:
                        messages.warning(
                            request, f"Resume uploaded successfully, but AI analysis failed: {ai_feedback.get('error')}")
                        if ai_feedback.get('raw_response'):
                            # Still save the resume but with error info
                            resume.ai_feedback = ai_feedback
                    else:
                        messages.success(
                            request, "Resume uploaded and analyzed successfully! Check the AI feedback for improvement suggestions.")

                except Exception as e:
                    messages.warning(
                        request, f"Resume uploaded successfully, but AI analysis encountered an error: {str(e)}")
                    resume.ai_feedback = {
                        'error': f'Analysis failed: {str(e)}'}

                resume.save()
                return redirect('resume_detail', pk=resume.pk)

            except Exception as e:
                messages.error(
                    request, f"An unexpected error occurred: {str(e)}")
        else:
            messages.error(
                request, "There was a problem with your upload. Please check the form and try again.")
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


def login_view(request):
    if request.user.is_authenticated:
        return redirect('resume_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('resume_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'resumes/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')


@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    # Define the sections for AI feedback display
    sections = ['summary', 'work_experience',
                'education', 'skills', 'projects']
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


@login_required
def regenerate_ai_feedback(request, pk):
    """Regenerate AI feedback for an existing resume."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    if not resume.text_content:
        messages.error(
            request, "Cannot regenerate AI feedback: No text content available for this resume.")
        return redirect('resume_detail', pk=pk)

    try:
        ai_feedback = analyze_resume_with_gemini(resume.text_content)
        resume.ai_feedback = ai_feedback

        if 'error' in ai_feedback:
            messages.warning(
                request, f"AI analysis failed: {ai_feedback.get('error')}")
        else:
            messages.success(request, "AI feedback regenerated successfully!")

        resume.save()

    except Exception as e:
        messages.error(request, f"Failed to regenerate AI feedback: {str(e)}")

    return redirect('resume_detail', pk=pk)


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


@login_required
def apply_rewrite(request, pk):
    """Apply a rewrite to a specific section of the resume."""
    if request.method == 'POST':
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        section = request.POST.get('section')
        improved_text = request.POST.get('improved_text')

        if not section or not improved_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Missing required data for applying rewrite.'})
            messages.error(
                request, "Missing required data for applying rewrite.")
            return redirect('resume_detail', pk=pk)

        try:
            # Update the AI feedback to mark this rewrite as applied
            if resume.ai_feedback and section in resume.ai_feedback:
                if 'applied_rewrites' not in resume.ai_feedback:
                    resume.ai_feedback['applied_rewrites'] = {}

                resume.ai_feedback['applied_rewrites'][section] = {
                    'text': improved_text,
                    'applied_at': str(datetime.now())
                }

                resume.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f"Rewrite applied to {section.replace('_', ' ').title()} section!"
                    })
                messages.success(
                    request, f"Rewrite applied to {section.replace('_', ' ').title()} section!")
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Could not find the specified section.'})
                messages.error(
                    request, "Could not find the specified section.")

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Failed to apply rewrite: {str(e)}'})
            messages.error(request, f"Failed to apply rewrite: {str(e)}")

        return redirect('resume_detail', pk=pk)

    return redirect('resume_detail', pk=pk)


@login_required
def improve_resume(request, pk):
    """Enhanced AI analysis and improvement interface for resumes."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    # Define the sections for AI feedback display
    sections = ['summary', 'work_experience',
                'education', 'skills', 'projects']
    return render(request, 'resumes/improve_resume.html', {
        'resume': resume,
        'sections': sections
    })
