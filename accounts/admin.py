from django.contrib import admin
from .models import User
from doctor.models import Clinic, MedicalRecord, DoctorProfile, Patients, AppointmentTimes, Appointments
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
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

# Inlines
class AssistantInline(admin.TabularInline):
    model = AssistantProfile
    fk_name = 'doctor'
    extra = 0
    fields = ('user',)
    can_delete = False
    show_change_link = True

class PatientsInline(admin.TabularInline):
    model = Patients
    fk_name = 'doctor'
    extra = 0
    fields = ('name', 'phone_number', 'gender', 'date_of_birth', 'date_added')
    readonly_fields = ('date_added',)
    show_change_link = True

class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 0
    fields = ('date', 'details', 'remarks', 'prescription')
    readonly_fields = ('date',)
    show_change_link = True

class AppointmentsInline(admin.TabularInline):
    model = Appointments
    extra = 0
    fields = ('date', 'start_time', 'status')
    show_change_link = True

# Admins
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'has_logo', 'admin', 'created_at')
    search_fields = ('name', 'address', 'phone_number', 'admin__username', 'admin__first_name', 'admin__last_name')
    list_filter = ('created_at',)

    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Logo?'

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'full_name', 'specialization', 'clinic', 'patients_count', 'assistants_count')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization', 'clinic__name')
    list_filter = ('specialization', 'clinic')
    ordering = ('user__username',)
    inlines = (PatientsInline,)
    list_select_related = ('user', 'clinic')

    def user_username(self, obj):
        return obj.user.username
    user_username.admin_order_field = 'user__username'
    user_username.short_description = 'Username'

    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.admin_order_field = 'user__first_name'

    def patients_count(self, obj):
        return obj.doctor_patients.count()

    def assistants_count(self, obj):
        return obj.assistants.count()

@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'gender', 'date_of_birth', 'doctor_name', 'clinic_name', 'date_added')
    search_fields = ('name', 'phone_number', 'doctor__user__username', 'doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    list_filter = ('gender', 'clinic', 'doctor__user__username')
    ordering = ('-date_added',)
    date_hierarchy = 'date_added'
    inlines = (MedicalRecordInline, AppointmentsInline)
    list_select_related = ('doctor__user', 'clinic')

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}" if (obj.doctor and obj.doctor.user) else '-'
    doctor_name.admin_order_field = 'doctor__user__first_name'

    def clinic_name(self, obj):
        return obj.clinic.name if obj.clinic else '-'
    clinic_name.admin_order_field = 'clinic__name'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'patient_name', 'doctor_name', 'clinic', 'short_details')
    search_fields = ('patient__name', 'doctor__user__username', 'doctor__user__first_name', 'doctor__user__last_name', 'details', 'prescription')
    list_filter = ('clinic', 'doctor__user__username')
    ordering = ('-date',)
    date_hierarchy = 'date'
    list_select_related = ('doctor__user', 'patient', 'clinic')

    def patient_name(self, obj):
        return obj.patient.name if obj.patient else '-'
    patient_name.admin_order_field = 'patient__name'

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}" if (obj.doctor and obj.doctor.user) else '-'
    doctor_name.admin_order_field = 'doctor__user__first_name'

    def short_details(self, obj):
        return (obj.details[:60] + '…') if len(obj.details) > 60 else obj.details
    short_details.short_description = 'Details'

@admin.register(AppointmentTimes)
class AppointmentTimesAdmin(admin.ModelAdmin):
    list_display = ('doctor_name', 'day_of_the_week', 'start_time', 'end_time', 'separation_time', 'activated_status')
    search_fields = ('doctor__user__username', 'doctor__user__first_name', 'doctor__user__last_name')
    list_filter = ('day_of_the_week', 'activated_status', 'doctor__user__username')
    ordering = ('doctor__user__username', 'day_of_the_week', 'start_time')
    actions = ('activate_selected', 'deactivate_selected')
    list_select_related = ('doctor__user',)

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}" if (obj.doctor and obj.doctor.user) else '-'
    doctor_name.admin_order_field = 'doctor__user__first_name'

    def activate_selected(self, request, queryset):
        updated = queryset.update(activated_status=True)
        self.message_user(request, f"{updated} appointment time(s) activated.")
    activate_selected.short_description = "Activate selected slots"

    def deactivate_selected(self, request, queryset):
        updated = queryset.update(activated_status=False)
        self.message_user(request, f"{updated} appointment time(s) deactivated.")
    deactivate_selected.short_description = "Deactivate selected slots"

@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'status', 'patient_name', 'doctor_name', 'clinic')
    search_fields = ('patient__name', 'doctor__user__username', 'doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    list_filter = ('status', 'date', 'clinic', 'doctor__user__username')
    ordering = ('-date', 'start_time')
    date_hierarchy = 'date'
    actions = ('mark_completed', 'mark_scheduled')
    list_select_related = ('doctor__user', 'patient', 'clinic')

    def patient_name(self, obj):
        return obj.patient.name if obj.patient else '-'
    patient_name.admin_order_field = 'patient__name'

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}" if (obj.doctor and obj.doctor.user) else '-'
    doctor_name.admin_order_field = 'doctor__user__first_name'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} appointment(s) marked as completed.")
    mark_completed.short_description = "Mark selected as completed"

    def mark_scheduled(self, request, queryset):
        updated = queryset.update(status='scheduled')
        self.message_user(request, f"{updated} appointment(s) marked as scheduled.")
    mark_scheduled.short_description = "Mark selected as scheduled"

@admin.register(AssistantProfile)
class AssistantProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'clinic_name', 'doctor_name')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'clinic__name', 'doctor__user__username')
    list_filter = ('clinic',)
    ordering = ('user__username',)
    list_select_related = ('user', 'clinic', 'doctor__user')
    filter_horizontal = ('doctors',)

    def username(self, obj):
        return obj.user.username
    username.admin_order_field = 'user__username'

    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.admin_order_field = 'user__first_name'

    def clinic_name(self, obj):
        return obj.clinic.name if obj.clinic else '-'

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}" if (obj.doctor and obj.doctor.user) else '-'

# Register custom User admin
admin.site.register(User, CustomUserAdmin)
