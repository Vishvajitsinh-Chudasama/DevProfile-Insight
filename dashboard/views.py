import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import AnalysisForm, JobPostForm, JobApplicationForm
from .models import ProfileAnalysis, JobPost, JobApplication, JobApplicationEvaluation
from .utils.evaluator import run_full_evaluation
from .utils.text_extractor import extract_text


@login_required
def personal(request):
    """
    Unified dashboard/personal page.
    Users upload a resume and get evaluation + GitHub analysis.
    """
    user = request.user
    if user.role != "personal":
        messages.error(request, "Only personal accounts can access this dashboard.")
        return redirect("company_dashboard")

    existing = ProfileAnalysis.objects.filter(user=user).last()
    form = AnalysisForm()

    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "run_analysis":
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
        elif action == "apply_job":
            application_form = JobApplicationForm(request.POST, request.FILES)
            if application_form.is_valid():
                job_id = request.POST.get("job_id")
                job = JobPost.objects.filter(id=job_id, is_active=True).first()
                if job:
                    if JobApplication.objects.filter(job=job, applicant=user).exists():
                        messages.info(request, "You already applied for this position.")
                    else:
                        resume_file = application_form.cleaned_data["resume"]
                        github_username = application_form.cleaned_data["github_username"]
                        cover_note = application_form.cleaned_data["cover_note"]

                        temp_saved_name = f"apply_{user.username}_{resume_file.name}"
                        temp_save_path = f"media/job_applications/resumes/{temp_saved_name}"
                        os.makedirs("media/job_applications/resumes", exist_ok=True)
                        with open(temp_save_path, "wb+") as dest:
                            for chunk in resume_file.chunks():
                                dest.write(chunk)
                        resume_text = extract_text(temp_save_path)

                        JobApplication.objects.create(
                            job=job,
                            applicant=user,
                            resume_file=resume_file,
                            resume_text=resume_text,
                            github_username=github_username,
                            cover_note=cover_note,
                        )
                        messages.success(request, "Application submitted successfully.")
                else:
                    messages.error(request, "Selected position is no longer available.")
                return redirect("personal_dashboard")

    open_jobs = JobPost.objects.filter(is_active=True).select_related("company")
    applied_job_ids = set(
        JobApplication.objects.filter(applicant=user).values_list("job_id", flat=True)
    )

    return render(request, 'personal_dashboard.html', {
        'form': form,
        'analysis': existing,
        'open_jobs': open_jobs,
        'applied_job_ids': applied_job_ids,
        'application_form': JobApplicationForm(),
    })


@login_required
def company_dashboard(request):
    user = request.user

    if user.role != "company":
        messages.error(request, "Only company accounts can access this dashboard.")
        return redirect("personal_dashboard")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_job":
            form = JobPostForm(request.POST)
            if form.is_valid():
                job_post = form.save(commit=False)
                job_post.company = user
                job_post.save()
                messages.success(request, "Position created successfully.")
                return redirect("company_dashboard")
        elif action == "delete_job":
            job_id = request.POST.get("job_id")
            job = JobPost.objects.filter(id=job_id, company=user).first()
            if job:
                job.delete()
                messages.success(request, "Position deleted successfully.")
            else:
                messages.error(request, "Position not found.")
            return redirect("company_dashboard")
    else:
        form = JobPostForm()

    if request.method != "POST" or request.POST.get("action") != "create_job":
        form = JobPostForm()

    company_jobs = JobPost.objects.filter(company=user).prefetch_related(
        "applications__applicant"
    )

    for job in company_jobs:
        role_requirement = " | ".join(
            [
                job.title or "",
                job.required_skills or "",
                job.description or "",
            ]
        ).strip()
        for application in job.applications.all():
            if not application.resume_text or not application.github_username:
                application.company_evaluation = None
                continue

            evaluation = JobApplicationEvaluation.objects.filter(
                application=application
            ).first()
            needs_refresh = (
                evaluation is None
                or evaluation.requirement_snapshot != role_requirement
                or evaluation.github_username != application.github_username
            )

            if needs_refresh:
                result = run_full_evaluation(
                    application.resume_text,
                    application.github_username,
                    role_requirement,
                )
                evaluation, _ = JobApplicationEvaluation.objects.update_or_create(
                    application=application,
                    defaults={
                        "requirement_snapshot": role_requirement,
                        "github_username": application.github_username,
                        "github_summary": result["github_summary"],
                        "score": result["score"],
                        "strengths": result["strengths"],
                        "weaknesses": result["weaknesses"],
                        "recommendations": result["recommendations"],
                    },
                )

            application.company_evaluation = evaluation

    return render(
        request,
        "company_dashboard.html",
        {
            "form": form,
            "company_jobs": company_jobs,
        },
    )
