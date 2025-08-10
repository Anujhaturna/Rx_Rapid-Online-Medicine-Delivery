
from django import forms
from .models import ManagerProfile
class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture']