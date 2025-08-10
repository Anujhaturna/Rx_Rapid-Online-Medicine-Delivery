from django.db import models
from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from django.db import models
from django.conf import settings  # ✅ for referencing custom user model

class ManagerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ use this instead of User
        on_delete=models.CASCADE,
        related_name='manager_profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.user.username})'



from medical.models import MediRegistration

class Notification(models.Model):
    SEND_CHOICES = [
        ('all', 'Send to All Medical Stores'),
        ('selected', 'Send to Selected Medical Store'),
    ]
    send_to = models.CharField(max_length=20, choices=SEND_CHOICES, default='all')
    medical_store = models.ForeignKey(MediRegistration, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    scheduled_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Notification to {self.send_to} stores"
