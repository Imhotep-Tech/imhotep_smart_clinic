from django.db import models
from django.conf import settings
from django.utils import timezone
from doctor.models import DoctorProfile

class AssistantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assistant_profile')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='assistants')
    
    def __str__(self):
        return f"Mr./Mrs. {self.user.get_full_name()}"