from django import forms
from .models import Messege

class MessegeForm(forms.ModelForm):
    class Meta:
        model = Messege
        fields = ['subject', 'description']



