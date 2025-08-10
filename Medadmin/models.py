from django.db import models

# Create your models here.
from django.db import models
# models.py
from django.db import models

from django.db import models

class Messege(models.Model):
    subject = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


# Create your models here.
