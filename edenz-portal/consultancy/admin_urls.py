from django.urls import path
from django.contrib.auth import views as auth_views
from . import admin_views
from .forms import AdminLoginForm  # Assuming the form is in forms.py

app_name = 'admin_portal'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(
        template_name='admin_portal/login.html',
        authentication_form=AdminLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('users/', admin_views.manage_users, name='manage_users'),
    path('users/approve/<int:user_id>/', admin_views.approve_user, name='approve_user'),
]