from django.db import models
from django.conf import settings
from django.utils import timezone

class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    clinic_photo_path = models.CharField(max_length=100, default='', null=True, blank=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Patients(models.Model):

    GENDER_CHOICES = (
        ('Male', 'male'),
        ('Female', 'female')
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='doctor_patients')
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Patient of {self.doctor})"

class MedicalRecord(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    details = models.CharField(max_length=20000)
    remarks = models.CharField(max_length=200)
    prescription = models.CharField(max_length=20000, default='', null=True, blank=True)

    def __str__(self):
        return f"Medical record for {self.patient} - {self.date.strftime('%Y-%m-%d')}"
    
class AppointmentTimes(models.Model):

    DAYS_OF_THE_WEEK = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    separation_time = models.DurationField(help_text="Duration between appointments (in minutes)")
    day_of_the_week = models.CharField(max_length=15, choices=DAYS_OF_THE_WEEK)
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
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    start_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    date = models.DateField()

    def __str__(self):
        return f"Appointment for Dr. {self.doctor.user.get_full_name()} and patient {self.patient} on {self.date}"

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        verbose_name_plural = "Appointments"