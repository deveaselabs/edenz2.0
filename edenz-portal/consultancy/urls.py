from django.urls import path
from .views import (
    add_student,
    view_students,
    edit_student,
    view_student,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('students/add/', add_student, name='add_student'),
    path('students/', view_students, name='view_students'),
    path('students/edit/<int:pk>/', edit_student, name='edit_student'),
    path('students/<int:pk>/', view_student, name='view_student'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)