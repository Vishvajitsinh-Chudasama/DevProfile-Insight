from django.shortcuts import render

# Create your views here.
def authentication_view(request):
    return render(request, 'choose_type.html')