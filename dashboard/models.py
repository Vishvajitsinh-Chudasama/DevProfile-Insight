# insight/models.py
from django.db import models
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


class JobPost(models.Model):
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_posts",
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    required_skills = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        company = self.company.company_name or self.company.username
        return f"{self.title} @ {company}"


class JobApplication(models.Model):
    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )
    resume_file = models.FileField(upload_to="job_applications/resumes/", blank=True)
    resume_text = models.TextField(blank=True)
    github_username = models.CharField(max_length=100, blank=True)
    cover_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "applicant"],
                name="unique_application_per_user_per_job",
            )
        ]

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"


class JobApplicationEvaluation(models.Model):
    application = models.OneToOneField(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="evaluation",
    )
    requirement_snapshot = models.TextField()
    github_username = models.CharField(max_length=100)
    github_summary = models.TextField()
    score = models.TextField()
    strengths = models.TextField()
    weaknesses = models.TextField()
    recommendations = models.TextField()
    evaluated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evaluation: {self.application}"
