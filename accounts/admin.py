from django.contrib import admin
from .models import User
from doctor.models import MedicalRecord, DoctorProfile, Patients, AppointmentTimes, Appointments
from assistant.models import AssistantProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Custom UserAdmin that includes password reset functionality
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'email_verify')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Imhotep Clinic info'), {'fields': ('user_type', 'email_verify')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # This adds the password change functionality to admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

# Register your models here
admin.site.register(MedicalRecord)
admin.site.register(DoctorProfile)
admin.site.register(Patients)
admin.site.register(AppointmentTimes)
admin.site.register(Appointments)
admin.site.register(AssistantProfile)
admin.site.register(User, CustomUserAdmin)  # Register with our custom admin class
