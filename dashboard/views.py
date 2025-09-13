from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import AnalysisForm
from .models import ProfileAnalysis
from .utils.evaluator import run_full_evaluation
from .utils.text_extractor import extract_text


@login_required
def personal(request):
    """
    Unified dashboard/personal page.
    Users upload a resume and get evaluation + GitHub analysis.
    """
    user = request.user
    existing = ProfileAnalysis.objects.filter(user=user).last()

    if request.method == 'POST':
        form = AnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = form.cleaned_data['resume']
            job_role = form.cleaned_data['job_role']
            github_username = form.cleaned_data['github_username']

            # Save uploaded resume
            saved_name = f"{user.username}_{resume_file.name}"
            save_path = f"media/resumes/{saved_name}"
            with open(save_path, 'wb+') as dest:
                for chunk in resume_file.chunks():
                    dest.write(chunk)

            # Extract and evaluate
            resume_text = extract_text(save_path)
            result = run_full_evaluation(resume_text, github_username, job_role)

            ProfileAnalysis.objects.create(
                user=user,
                job_role=job_role,
                github_username=github_username,
                resume_file=saved_name,
                resume_text=resume_text,
                github_summary=result["github_summary"],
                score=result["score"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                recommendations=result["recommendations"],
            )
            return redirect('personal_dashboard')
    else:
        form = AnalysisForm()

    return render(request, 'personal_dashboard.html', {
        'form': form,
        'analysis': existing,
    })
