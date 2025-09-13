from django.urls import path
from . import views

urlpatterns = [
    path("personal/", views.personal, name="personal_dashboard"), 
]

