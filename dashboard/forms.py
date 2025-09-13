# insight/forms.py
from django import forms

class AnalysisForm(forms.Form):
    resume = forms.FileField(label="Upload Resume (PDF or DOCX)")
    job_role = forms.CharField(label="Target Job Role", max_length=100)
    github_username = forms.CharField(label="GitHub Username", max_length=100)
