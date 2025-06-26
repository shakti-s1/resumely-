from django.urls import path
from . import views
from rest_framework.permissions import IsAuthenticated

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('register/', views.register, name='register'),
    path('<int:pk>/', views.resume_detail, name='resume_detail'),
    path('<int:pk>/edit/', views.edit_resume, name='edit_resume'),
    path('<int:pk>/delete/', views.delete_resume, name='delete_resume'),
    path('profile/', views.profile, name='profile'),
    # API endpoint for resume analysis
    path('api/analyze-resume/', views.ResumeAnalysisAPIView.as_view(),
         name='api_analyze_resume'),
]
