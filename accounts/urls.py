from django.urls import path
from . import views

urlpatterns = [
    path("", views.authentication_view, name="authentication"), 
    path('signup/personal/', views.personal_signup, name='personal_signup'),
    path('signup/company/', views.company_signup, name='company_signup'),
    path('login/',views.login,name='login')
]

