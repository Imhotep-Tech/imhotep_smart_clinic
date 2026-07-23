from django.db import models
from django.conf import settings
from django.utils import timezone

class Clinic(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    logo = models.CharField(max_length=200, default='', null=True, blank=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_clinics')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    clinic_photo_path = models.CharField(max_length=100, default='', null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctors', null=True, blank=True)

    @property
    def logo_path(self):
        if self.clinic and self.clinic.logo:
            return self.clinic.logo
        return self.clinic_photo_path or ''

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

class Patients(models.Model):

    GENDER_CHOICES = (
        ('Male', 'male'),
        ('Female', 'female')
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_profile')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='clinic_patients', null=True, blank=True)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_patients')
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        clinic_str = self.clinic.name if self.clinic else "No Clinic"
        return f"{self.name} ({clinic_str})"

class MedicalRecord(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    details = models.CharField(max_length=2000, help_text="Clinical notes - visible to doctor and assistant only")
    remarks = models.CharField(max_length=1000, default='', blank=True, help_text="Visible to patient")
    prescription = models.CharField(max_length=1000, default='', null=True, blank=True, help_text="Visible to patient")

    def __str__(self):
        return f"Medical record for {self.patient} - {self.date.strftime('%Y-%m-%d')}"

class AppointmentTimes(models.Model):

    DAYS_OF_THE_WEEK = (
        ('Monday', 'monday'),
        ('Tuesday', 'tuesday'),
        ('Wednesday', 'wednesday'),
        ('Thursday', 'thursday'),
        ('Friday', 'friday'),
        ('Saturday', 'saturday'),
        ('Sunday', 'sunday')
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    separation_time = models.DurationField(help_text="Duration between appointments (in minutes)")
    day_of_the_week = models.CharField(max_length=10, choices=DAYS_OF_THE_WEEK)
    activated_status = models.BooleanField(default=True, help_text="Whether this appointment slot is currently active")

    def __str__(self):
        status = "active" if self.activated_status else "inactive"
        return f"Appointment times for Dr. {self.doctor.user.get_full_name()} on {self.day_of_the_week} ({status})"

class Appointments(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    start_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    date = models.DateField()

    def __str__(self):
        return f"Appointment for Dr. {self.doctor.user.get_full_name()} and patient {self.patient} on {self.date}"

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        verbose_name_plural = "Appointments"