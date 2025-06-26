from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='resumes/')
    text_content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_feedback = models.JSONField(null=True, blank=True,
                                   help_text="Structured AI feedback for this resume.")

    def __str__(self):
        return f"{self.title} ({self.user.username})"
