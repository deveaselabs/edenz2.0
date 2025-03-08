from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    # Authentication
    path('register/', views.business_register, name='register'),
    path('login/', views.BusinessLoginView.as_view(), name='login'),
    path('logout/', views.BusinessLogoutView.as_view(), name='logout'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    # Dashboard & Students
    path('dashboard/', views.business_dashboard, name='dashboard'),
    path('students/', views.view_students, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:pk>/', views.view_student, name='student_detail'),
    path('students/<int:pk>/edit/', views.edit_student, name='edit_student'),
    
    # Chat Functionality
    path('students/<int:student_id>/chat/', 
         views.student_chat, 
         name='student_chat'),
]