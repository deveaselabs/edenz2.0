from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import FieldTracker

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('BUSINESS', 'Consultancy Business'),
        ('PROCESSING', 'Processing Team'),
        ('ADMIN', 'System Admin'),
        ('STUDENT', 'Student')  # Add student type
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='BUSINESS')
    approved = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    tracker = FieldTracker(fields=['approved'])

    def save(self, *args, **kwargs):
        if self.user_type == 'STUDENT':
            self.is_student = True
        super().save(*args, **kwargs)

class BusinessProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name
    
class Student(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='student_profile')
    business = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='students')
    name_of_applicant = models.CharField(max_length=255)
    email = models.EmailField()
    program_of_interest = models.CharField(max_length=200)
    application_date = models.DateTimeField(auto_now_add=True)
    
    # Additional fields (all optional)
    father_name = models.CharField(max_length=255, blank=True)
    student_cnic = models.CharField(max_length=15, blank=True)
    fathers_occupation = models.CharField(max_length=100, blank=True)
    fathers_cnic = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_no = models.CharField(max_length=20, blank=True)
    passport_no = models.CharField(max_length=50, blank=True)
    name_of_country = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        permissions = [
            ("processing_edit_student", "Can edit student details as processing team"),
        ]

    def __str__(self):
        return f"{self.name_of_applicant} - {self.email}"
    
    
class Document(models.Model):
    DOCUMENT_TYPES = (
        ('PASSPORT', 'Passport'),
        ('ID_CARD', 'National ID Card'),
        ('MATRIC', 'Matric/O-Level Certificate'),
        ('FSC', 'FSC/A-Level Certificate'),
        ('DAE', 'DAE Certificate'),
        ('BACH_DEGREE', 'Bachelor\'s Degree'),
        ('BACH_TRANSCRIPT', 'Bachelor\'s Transcript'),
        ('MASTER_DEGREE', 'Master\'s/MPhil Degree'),
        ('MASTER_TRANSCRIPT', 'Master\'s/MPhil Transcript'),
        ('LOR', 'Letter of Recommendation'),
        ('SOP', 'Statement of Purpose'),
        ('EXP_CERT', 'Experience Certificate'),
        ('MEDICAL', 'Medical Certificate'),
        ('CV', 'CV/Resume'),
        ('PROJECTS', 'Soft Copies of Projects'),
        ('PUBLICATIONS', 'International Publications'),
        ('CUSTOM', 'Custom Document'),
    )

    student = models.ForeignKey(Student,related_name="documents", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.student.name_of_applicant}"
    
    
class ProcessingTeamProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    can_review_applications = models.BooleanField(default=True)
    can_approve_applications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.email} - {self.job_title}"
    
    
    
    
    
    
class StudentDiscussion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    business = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    processing_officer = models.ForeignKey(CustomUser, related_name='discussions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DiscussionMessage(models.Model):
    discussion = models.ForeignKey(StudentDiscussion, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    document = models.FileField(upload_to='discussion_docs/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
class DocumentRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=Document.DOCUMENT_TYPES)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(upload_to='document_versions/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    
    
class StudentUpdateLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField()

    def __str__(self):
        return f"{self.student} updated by {self.updated_by}"
    
    
    
    
    
    
class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    can_manage_users = models.BooleanField(default=True)
    can_manage_content = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.department}"