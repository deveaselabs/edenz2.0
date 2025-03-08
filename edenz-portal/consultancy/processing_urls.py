from django.urls import path
from . import views

app_name = 'processing'

urlpatterns = [
    # Authentication
    path('register/', views.processing_team_register, name='register'),
    path('login/', views.ProcessingLoginView.as_view(), name='login'),
    path('logout/', views.ProcessingLogoutView.as_view(), name='logout'),
    
    # Dashboard & Workflow
    path('dashboard/', views.processing_dashboard, name='dashboard'),
    path('businesses/', views.business_list, name='business_list'),
    path('business/<int:business_id>/students/', 
         views.business_students, 
         name='business_students'),
    
    # Chat Functionality
    path('students/<int:student_id>/chat/', 
         views.student_chat, 
         name='student_chat'),
    path('students/<int:student_id>/edit/',
         views.processing_edit_student,
         name='edit_student'),
    path('students/<int:student_id>/',
         views.processing_student_detail,
         name='student_detail'),
]