from django.db import models
from django.conf import settings
from django.utils import timezone
from doctor.models import DoctorProfile

class AssistantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assistant_profile')
    clinic = models.ForeignKey('doctor.Clinic', on_delete=models.CASCADE, related_name='clinic_assistants', null=True, blank=True)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assistants')
    doctors = models.ManyToManyField(DoctorProfile, related_name='multi_assistants', blank=True)
    
    def __str__(self):
        return f"Assistant {self.user.get_full_name() or self.user.username}"