# customer/forms.py

from django import forms
from .models import CustomerUser


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomerUser
        fields = ['email', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300',
                'placeholder': 'Enter your email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300',
                'placeholder': 'Enter your phone number'
            }),
        }


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        label="Enter OTP",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300',
            'placeholder': '6-digit code',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise forms.ValidationError("OTP must be numeric.")
        if len(otp) != 6:
            raise forms.ValidationError("OTP must be exactly 6 digits.")
        return otp


# forms.py

from django import forms
from medical.models import Medicine



class PrescriptionForm(forms.Form):
    # You can add more fields depending on your needs
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    # Add more fields as required, such as the upload prescription file, etc.


# forms.py

from django import forms
from .models import CustomerUser

# forms.py

from django import forms
from .models import CustomerUser


from django import forms
from .models import CustomerUser
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerUser
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 p-2 focus:ring-2 focus:ring-green-500 focus:outline-none'}),
            'phone': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 p-2 focus:ring-2 focus:ring-green-500 focus:outline-none'}),
            'address': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 p-2 focus:ring-2 focus:ring-green-500 focus:outline-none'}),
        }



from django import forms
from django import forms
from .models import ShippingDetails
from django.contrib.auth.models import User


class ShippingDetailsForm(forms.ModelForm):
    class Meta:
        model = ShippingDetails
        fields = ['full_name', 'phone_number', 'address', 'city', 'email']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['phone_number'].initial = user.profile.phone_number
            self.fields['address'].initial = user.profile.address
            self.fields['email'].initial = user.email
            self.fields['city'].initial = "Amravati"  # Set city as default

    # You can add custom validation for the address if needed
    def clean_address(self):
        address = self.cleaned_data.get('address')
        # Add address validation if necessary
        return address



# Customer/forms.py
from django import forms
from .models import CustomerIssue

class CustomerIssueForm(forms.ModelForm):
    class Meta:
        model = CustomerIssue
        fields = ['subject', 'description', 'contact']
