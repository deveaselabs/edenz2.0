from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from .forms import BusinessRegistrationForm,StudentRegistrationForm,StudentEditForm,DocumentFormSet,ProcessingTeamRegistrationForm,ProcessingStudentForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .models import Student,CustomUser,DiscussionMessage,StudentDiscussion,Document,DocumentRequest,DocumentVersion,StudentUpdateLog
from .mixins import BusinessRequiredMixin
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth.views import LogoutView
from django.core.exceptions import PermissionDenied
import os
from datetime import datetime
from django.shortcuts import render

def landing(request):
    # Redirect authenticated users to appropriate dashboards
    if request.user.is_authenticated:
        if request.user.user_type == 'BUSINESS':
            return redirect('business:dashboard')
        elif request.user.user_type == 'PROCESSING':
            return redirect('processing:dashboard')
        elif request.user.is_superuser:
            return redirect('admin:index')
    return render(request, 'landing.html')

# Businessresgitartion

def business_register(request):
    if request.method == 'POST':
        form = BusinessRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            
            # Remove automatic login
            messages.info(request, 'Your registration is under review. We will email you once approved.')
            return redirect('business:pending_approval')
            
    else:
        form = BusinessRegistrationForm()
    return render(request, 'registration/business_register.html', {'form': form})

def pending_approval(request):
    return render(request, 'registration/pending_approval.html')
# login view for business
def business_check(user):
        return user.is_authenticated and user.user_type == 'BUSINESS' and user.approved
def processing_check(user):
    return user.is_authenticated and user.user_type == 'PROCESSING' and user.approved

def approval_page(request):
    return render(request, 'business/approval_page.html')

class BusinessLoginView(auth_views.LoginView):
    template_name = 'registration/business_login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.approved:
            messages.error(self.request, 'Your account is still pending approval')
            return self.form_invalid(form)
        if user.user_type != 'BUSINESS':
            messages.error(self.request, 'Invalid account type')
            return self.form_invalid(form)
        login(self.request, user)
        return redirect('business:dashboard')
    
class BusinessLogoutView(LogoutView):
    def get_next_page(self):
        return reverse('business:login')


@user_passes_test(business_check, login_url='business:login')
def business_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('business:login')
    students = Student.objects.filter(business=request.user)
    discussions = StudentDiscussion.objects.filter(business=request.user)
    
    context = {
        'total_students': students.count(),
        'active_discussions': discussions.count(),
        'pending_documents': DiscussionMessage.objects.filter(
            discussion__in=discussions,
            document__isnull=False,
            read=False
        ).exclude(sender=request.user).count(),
        'recent_discussions': discussions.order_by('-updated_at')[:5]
    }
    return render(request, 'business/dashboard.html', context)
@login_required
@user_passes_test(business_check, login_url='business:login')
def add_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                student = form.save(commit=False)  # Don't save yet
                
                # ✅ Assign required fields
                student.business = request.user  # Business is the logged-in user
                
                # ✅ Create a CustomUser instance for the student
                student_user = CustomUser.objects.create(
                    username=form.cleaned_data['email'],  # Assuming email is the username
                    email=form.cleaned_data['email']
                )
                
                student.user = student_user  # Link student to newly created CustomUser
                
                student.save()  # Now save the student with required fields

                messages.success(request, "Student created successfully!")
                return redirect('business:student_list')
            except IntegrityError:
                messages.error(request, 'A student with this email already exists!')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'business/add_student.html', {'form': form})



@login_required
@user_passes_test(business_check, login_url='business:login')
def view_students(request):
    students = Student.objects.filter(business=request.user)
    return render(request, 'business/students_list.html', {'students': students})

@login_required
@user_passes_test(business_check, login_url='business:login')
def view_student(request, pk):
    student = get_object_or_404(
        Student.objects.select_related('user').prefetch_related('documents'), 
        pk=pk, 
        business=request.user
    )
    return render(request, 'business/student_detail.html', {
        'student': student,
        'documents': student.documents.all()
    })



class StudentListView(BusinessRequiredMixin, ListView):
    model = Student
    template_name = 'business/students_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.filter(business=self.request.user)
    
    
@login_required
@user_passes_test(business_check, login_url='business:login')
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk, business=request.user)
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        document_formset = DocumentFormSet(
            request.POST, 
            request.FILES, 
            instance=student
        )
        
        if form.is_valid() and document_formset.is_valid():
            form.save()
            documents = document_formset.save(commit=False)
            for doc in documents:
                doc.student = student
                doc.save()
            for form in document_formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()
            messages.success(request, 'Student updated successfully!')
            return redirect('business:student_detail', pk=student.id)
    else:
        form = StudentEditForm(instance=student)
        document_formset = DocumentFormSet(instance=student)
    
    return render(request, 'business/edit_student.html', {
        'form': form,
        'document_formset': document_formset,
        'student': student
    })
    
    
    
def processing_team_register(request):
    if request.method == 'POST':
        form = ProcessingTeamRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration submitted for admin approval')
            return redirect('processing:login')
    else:
        form = ProcessingTeamRegistrationForm()
    return render(request, 'registration/processing_register.html', {'form': form})

class ProcessingLoginView(auth_views.LoginView):
    template_name = 'registration/processing_login.html'
    
    def get_success_url(self):
        return reverse('processing:dashboard')
    
class ProcessingLogoutView(LogoutView):
    def get_next_page(self):
        return reverse('processing:login')

@user_passes_test(processing_check, login_url='processing:login')
def processing_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('processing:login')
    context = {
        'total_businesses': CustomUser.objects.filter(user_type='BUSINESS', approved=True).count(),
        'active_cases': StudentDiscussion.objects.filter(processing_officer=request.user).count(),
        'pending_reviews': DiscussionMessage.objects.filter(
            discussion__processing_officer=request.user,
            read=False
        ).exclude(sender=request.user).count(),
        'recent_messages': DiscussionMessage.objects.filter(
            discussion__processing_officer=request.user
        ).order_by('-timestamp')[:5],
        'team_member': request.user.processingteamprofile
    }
    return render(request, 'processing/dashboard.html', context)












@login_required
@user_passes_test(processing_check, login_url='processing:login')
def business_list(request):
    businesses = CustomUser.objects.filter(user_type='BUSINESS', approved=True)
    return render(request, 'processing/business_list.html', {'businesses': businesses})

@login_required
@user_passes_test(processing_check, login_url='processing:login')
def business_students(request, business_id):
    business = get_object_or_404(CustomUser, id=business_id)
    students = Student.objects.filter(business=business)
    return render(request, 'processing/student_list.html', {
        'business': business,
        'students': students
    })
@login_required
@user_passes_test(processing_check, login_url='processing:login')
def student_discussion(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    discussion, created = StudentDiscussion.objects.get_or_create(
        student=student,
        defaults={
            'business': student.business,
            'processing_officer': request.user
        }
    )
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        document = request.FILES.get('document', None)  # ✅ Set a default value (None)

        if document:
            ext = os.path.splitext(document.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                messages.error(request, 'Invalid file format')  # noqa: F823
                return redirect('processing:student_discussion', student_id=student_id)
        
        # ✅ Move this block inside `if request.method == 'POST'`
        DiscussionMessage.objects.create(
            discussion=discussion,
            sender=request.user,
            message=message,
            document=document  # ✅ This will be None if no file is uploaded
        )
        return redirect('processing:student_discussion', student_id=student_id)
    
    messages = discussion.messages.all().order_by('timestamp')
    return render(request, 'processing/discussion.html', {
        'student': student,
        'messages': messages,
        'discussion': discussion
    })

@login_required
def student_chat(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Permission checks
    if request.user.user_type == 'BUSINESS' and student.business != request.user:
        raise PermissionDenied
        
    # For processing team, create discussion if it doesn't exist rather than blocking access
    discussion = None
    if request.user.user_type == 'PROCESSING':
        discussion, created = StudentDiscussion.objects.get_or_create(
            student=student,
            defaults={
                'business': student.business,
                'processing_officer': request.user
            }
        )
    else:  # BUSINESS user
        discussion = StudentDiscussion.objects.filter(student=student).first()
        if not discussion:
            # Create new discussion with first available processing officer
            processing_officer = CustomUser.objects.filter(
                user_type='PROCESSING', 
                approved=True,
                processingteamprofile__isnull=False
            ).first()
            if processing_officer:
                discussion = StudentDiscussion.objects.create(
                    student=student,
                    business=request.user,
                    processing_officer=processing_officer
                )
            else:
                messages.error(request, "No processing officers available. Please try again later.")
                return redirect('business:student_detail', pk=student_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_message':
            message_text = request.POST.get('message', '')
            document = request.FILES.get('document')
            message = DiscussionMessage.objects.create(
                discussion=discussion,
                sender=request.user,
                message=message_text,
                document=document
            )
            
            if document:
    # Save the uploaded file to the DiscussionMessage directly
                message.document = document  
                message.save()

    # Optionally, also store the document in a separate Document model
                Document.objects.create(
                    student=student,
                    document_type='CUSTOM',  # Or get from form
                file=document  # Keep this as an actual file
                )
            messages.success(request, 'Message sent successfully')
        
        elif action == 'request_document':
            doc_type = request.POST.get('document_type')
            due_date = request.POST.get('due_date')
            try:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                due_date = None
            DocumentRequest.objects.create(
                student=student,
                requested_by=request.user,
                document_type=doc_type,
                due_date=due_date
            )
            messages.success(request, 'Document request sent successfully')
        
        elif action == 'update_document':
            document_id = request.POST.get('document_id')
            new_file = request.FILES.get('new_file')
            comment = request.POST.get('comment', '')
            try:
                document = Document.objects.get(id=document_id)
                DocumentVersion.objects.create(
                    document=document,
                    file=new_file,
                    uploaded_by=request.user,
                    comment=comment
                )
                messages.success(request, 'Document updated successfully')
            except (Document.DoesNotExist, ValueError):
                messages.error(request, 'Invalid document selected')

        return redirect('business:student_chat', student_id=student_id)

    context = {
        'student': student,
        'discussion': discussion,
        'messages': discussion.messages.all().order_by('timestamp'),
        'document_requests': DocumentRequest.objects.filter(student=student),
        'documents': Document.objects.filter(student=student)
    }
    return render(request, 'chat/student_chat.html', context)

def processing_check(user):
    return user.is_authenticated and \
           user.user_type == 'PROCESSING' and \
           user.approved and \
           hasattr(user, 'processingteamprofile')

@login_required
@user_passes_test(processing_check, login_url='processing:login')
# @permission_required('consultancy.processing_edit_student', raise_exception=True)
def processing_edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if not StudentDiscussion.objects.filter(
        student=student, 
        processing_officer=request.user
    ).exists():
        raise PermissionDenied

    if request.method == 'POST':
        form = ProcessingStudentForm(request.POST, instance=student)
        if form.is_valid():
            # Track changes before saving
            changes = {}
            for field in form.changed_data:
                changes[field] = {
                    'old': form.initial.get(field),
                    'new': form.cleaned_data.get(field)
                }
            
            if changes:
                StudentUpdateLog.objects.create(
                    student=student,
                    updated_by=request.user,
                    changes=changes
                )
            
            form.save()
            messages.success(request, 'Student details updated successfully')
            return redirect('processing:student_detail', student_id=student_id)
    else:
        form = ProcessingStudentForm(instance=student)
    
    return render(request, 'processing/edit_student.html', {
        'form': form,
        'student': student
    })
    
    
@login_required
@user_passes_test(processing_check, login_url='processing:login')
# @permission_required('consultancy.processing_edit_student', raise_exception=True)
def processing_student_detail(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related('business')
                       .prefetch_related('documents', 'documents__versions'),
        id=student_id
    )
    
    # Verify processing officer access
    if not StudentDiscussion.objects.filter(
        student=student, 
        processing_officer=request.user
    ).exists():
        raise PermissionDenied

    documents = student.documents.all()
    update_logs = StudentUpdateLog.objects.filter(student=student).order_by('-updated_at')
    
    return render(request, 'processing/student_detail.html', {
        'student': student,
        'documents': documents,
        'update_logs': update_logs
    })
    
