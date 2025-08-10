from django import forms
from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message', 'scheduled_date']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
        }
