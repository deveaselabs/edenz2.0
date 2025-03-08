from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import CustomUser, BusinessProfile,Student,Document,ProcessingTeamProfile,AdminProfile
import os

class BusinessRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = "Minimum 8 characters"
    company_name = forms.CharField(max_length=200)
    license_number = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea)
    phone_number = forms.CharField(max_length=20)
    website = forms.URLField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2',
                  'company_name', 'license_number', 'address',
                  'phone_number', 'website']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'BUSINESS'
        if commit:
            user.save()
            BusinessProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                license_number=self.cleaned_data['license_number'],
                address=self.cleaned_data['address'],
                phone_number=self.cleaned_data['phone_number'],
                website=self.cleaned_data['website']
            )
        return user
class StudentRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].help_text = "Minimum 8 characters"
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter student's login password",
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Confirm the password"
    )

    class Meta:
        model = Student
        fields = ['name_of_applicant', 'email', 'program_of_interest']
        unique_together = ['business','email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long!")
        
        return cleaned_data

class StudentEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Student
        exclude = ['user', 'business', 'application_date']
        # Include all other fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        # Update user email
        student.user.email = self.cleaned_data['email']
        student.user.username = self.cleaned_data['email']
        student.user.save()
        
        if commit:
            student.save()
        return student
        
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'multiple': False}),
        }
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise forms.ValidationError('Unsupported file format.')
        return file

DocumentFormSet = inlineformset_factory(
    Student, Document, form=DocumentForm,
    extra=1, can_delete=True, max_num=20
)


def save(self, commit=True, business=None):
    # Create user first
    email = self.cleaned_data['email']
    password = self.cleaned_data['password']
    
    user = CustomUser.objects.create_user(
        username=email,
        email=email,
        password=password,
        user_type='STUDENT',
        is_student=True
    )
    
    # Create student profile
    student = super().save(commit=False)
    student.user = user
    student.business = business
    
    if commit:
        student.save()
    
    return student


class ProcessingTeamRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    job_title = forms.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'department', 'job_title']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'PROCESSING'
        user.approved = False  # Requires admin approval
        if commit:
            user.save()
            ProcessingTeamProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                job_title=self.cleaned_data['job_title']
            )
        return user
    
class ProcessingStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['business', 'application_date']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'application_date': forms.DateTimeInput(attrs={'disabled': True}),
            'last_updated': forms.DateTimeInput(attrs={'disabled': True}),
        }
        labels = {
            'name_of_applicant': 'Full Name',
            'student_cnic': 'Student CNIC',
            'fathers_cnic': "Father's CNIC"
        }
        
class AdminRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'department']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'ADMIN'
        user.is_staff = True
        if commit:
            user.save()
            AdminProfile.objects.create(
                user=user,
                department=self.cleaned_data['department']
            )
        return user

class AdminLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_staff or user.user_type != 'ADMIN':
            raise ValidationError("Invalid admin credentials")