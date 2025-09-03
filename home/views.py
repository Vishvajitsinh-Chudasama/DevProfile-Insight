from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def Features(request):
    return render(request, 'Features.html')