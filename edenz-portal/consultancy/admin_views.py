from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, BusinessProfile, ProcessingTeamProfile, Student

def admin_check(user):
    return user.is_authenticated and user.user_type == 'ADMIN' and user.is_staff


@user_passes_test(admin_check, login_url='/admin-portal/login/')
def admin_dashboard(request):
    stats = {
        'total_businesses': BusinessProfile.objects.count(),
        'total_processing_staff': ProcessingTeamProfile.objects.count(),
        'total_students': Student.objects.count(),
        'pending_approvals': CustomUser.objects.filter(approved=False).count()
    }
    return render(request, 'admin_portal/dashboard.html', {'stats': stats})


@user_passes_test(admin_check)
def manage_users(request):
    users = CustomUser.objects.all().select_related(
        'businessprofile', 
        'processingteamprofile',
        'adminprofile'
    )
    return render(request, 'admin_portal/manage_users.html', {'users': users})

@login_required
@user_passes_test(admin_check)
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.approved = True
        user.save()
        # Send approval email
    return redirect('admin_portal:manage_users')