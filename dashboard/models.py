# insight/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings  

class ProfileAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    github_username = models.CharField(max_length=100)
    resume_file = models.FileField(upload_to='resumes/')
    resume_text = models.TextField()         # extracted plain text
    github_summary = models.TextField()
    score = models.TextField()
    strengths = models.TextField()
    weaknesses = models.TextField()
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_role}"
