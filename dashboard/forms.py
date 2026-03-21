# insight/forms.py
from django import forms
from .models import JobPost

class AnalysisForm(forms.Form):
    resume = forms.FileField(label="Upload Resume (PDF or DOCX)")
    job_role = forms.CharField(label="Target Job Role", max_length=100)
    github_username = forms.CharField(label="GitHub Username", max_length=100)


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ["title", "description", "required_skills", "location", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "required_skills": forms.Textarea(attrs={"rows": 4}),
        }


class JobApplicationForm(forms.Form):
    resume = forms.FileField(label="Resume for this application")
    github_username = forms.CharField(label="GitHub Username", max_length=100)
    cover_note = forms.CharField(
        label="Cover Note (Optional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
