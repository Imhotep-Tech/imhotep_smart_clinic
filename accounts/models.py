from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Base user model for all user types in the clinic system
    """
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('assistant', 'Assistant'),
        ('patient', 'Patient'),
        ('clinic_admin', 'Clinic Admin'),
        ('super_admin', 'Super Admin')
    )
    
    email_verify = models.BooleanField(default=False)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    is_demo = models.BooleanField(default=False)
    
    def is_doctor(self):
        return self.user_type == 'doctor'
        
    def is_assistant(self):
        return self.user_type == 'assistant'

    def is_patient(self):
        return self.user_type == 'patient'

    def is_clinic_admin(self):
        return self.user_type == 'clinic_admin'

    def is_super_admin(self):
        return self.user_type == 'super_admin' or self.is_superuser
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"