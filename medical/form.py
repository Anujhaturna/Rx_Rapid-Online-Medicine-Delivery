from django import forms
from .models import MediRegistration

from django import forms
from django.forms import inlineformset_factory
from .models import Medicine

class MedRegistrationForm(forms.ModelForm):
    class Meta:
        model = MediRegistration
        fields = [
            'store_name',
            'owner_name', 'owner_photo', 'owner_id_proof',
            'pharmacist_name', 'pharmacist_photo',
            'address', 'street_address', 'city', 'state', 'pincode',
            'contact', 'email', 'shop_no',
            'license_no', 'license_photo', 'intimation_letter_photo', 'food_license_photo',
            'bank_account_no', 'ifsc_code', 'passbook_photo',
            'username', 'password',  # Added username and password fields
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'street_address': forms.Textarea(attrs={'rows': 2}),
            'state': forms.Select(),
            'password': forms.PasswordInput(),  # Use password input widget for password field
        }

        def clean_email(self):
            email = self.cleaned_data.get('email')
            if MediRegistration.objects.filter(email=email).exists():
                raise forms.ValidationError("Email already exists.")
            return email

        def clean_username(self):
            username = self.cleaned_data.get('username')
            if MediRegistration.objects.filter(username=username).exists():
                raise forms.ValidationError("Username already exists.")
            return username

        def save(self, commit=True):
            instance = super().save(commit=False)
            # Hash password before saving it
            if instance.password:
                instance.password = instance.password  # In real case, you should hash it using `instance.set_password(password)`
            if commit:
                instance.save()
            return instance


class LoginForm(forms.Form):
            username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
                'placeholder': 'Enter username',
                'class': 'form-control'
            }))
            password = forms.CharField(widget=forms.PasswordInput(attrs={
                'placeholder': 'Enter password',
                'class': 'form-control'
            }))
class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name',
            'brand',
            'description',
            'price',
            'quantity_in_stock',
            'expiry_date',
            'medicine_image',  # ✅ Added image field
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }



from django import forms
from .models import PrescriptionBillItem

class PrescriptionBillItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionBillItem
        fields = ['medicine_name', 'batch_number', 'expiry_date', 'mrp', 'quantity']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'medicine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

