from django.shortcuts import render, redirect
from django.contrib import messages
from .form import PersonalSignupForm, CompanySignupForm
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.
def authentication_view(request):
    if request.method == "POST":
        role = request.POST.get("user_type")
        if role == "personal":
            return redirect("personal_signup")
        elif role == "company":
            return redirect("company_signup")
    return render(request, 'choose_type.html')

def personal_signup(request):
    if request.method == "POST":
        form = PersonalSignupForm(request.POST)
        if form.is_valid():
            form.save()            
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PersonalSignupForm()
    return render(request, 'personal_signup.html', {'form': form})


def company_signup(request):
    if request.method == "POST":
        form = CompanySignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CompanySignupForm()
    return render(request, 'company_signup.html', {'form': form})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            
            if user.role == "personal":
                return redirect("personal_dashboard")
            elif user.role == "company":
                return redirect("company_dashboard") 
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")