from django.contrib import admin
from .models import CustomUser, BusinessProfile, Student,Document,AdminProfile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'approved', 'date_joined')
    list_filter = ('user_type', 'approved')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        for user in queryset:
            if not user.approved and user.user_type == 'BUSINESS':
                user.approved = True
                user.save()  # This will trigger the signal
        self.message_user(request, f"{queryset.count()} business accounts approved")

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'license_number', 'registration_date')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'name_of_applicant', 'father_name', 'passport_no',
        'contact_no', 'name_of_country'
    )
    search_fields = ('name_of_applicant', 'passport_no', 'contact_no')
    list_filter = ('name_of_country', 'program_of_interest')
    
admin.site.register(Document)
admin.site.register(AdminProfile)