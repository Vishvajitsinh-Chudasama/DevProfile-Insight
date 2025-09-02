from django.urls import path
from . import views

urlpatterns = [
    path("", views.authentication_view, name="authentication"), 
]

