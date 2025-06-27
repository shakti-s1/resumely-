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
    path('<int:pk>/regenerate-ai/', views.regenerate_ai_feedback,
         name='regenerate_ai_feedback'),
    path('<int:pk>/apply-rewrite/', views.apply_rewrite, name='apply_rewrite'),
    path('<int:pk>/improve/', views.improve_resume, name='improve_resume'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # API endpoint for resume analysis
    path('api/analyze/', views.ResumeAnalysisAPIView.as_view(),
         name='resume_analysis_api'),
]
