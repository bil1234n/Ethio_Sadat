from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os
from .models import UserProfile

class AdminRegistrationForm(UserCreationForm):
    passcode = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Secret Passcode'}),
        required=True,
        help_text="Requires authorization passcode."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def clean_passcode(self):
        passcode = self.cleaned_data.get('passcode')
        # Fetch the real passcode from the .env file
        correct_passcode = os.environ.get('ADMIN_REGISTER_PASSCODE')
        
        if not correct_passcode:
            raise ValidationError("Server configuration error: Passcode not set in .env")
        
        if passcode != correct_passcode:
            raise ValidationError("Invalid Admin Passcode! Access Denied.")
            
        return passcode
    

class UserUpdateForm(forms.ModelForm):
     # Explicitly define username as disabled
    username = forms.CharField(
        disabled=True, 
        help_text="Your username cannot be changed."
    )
    
    # Explicitly add email and make it required (optional, but good practice)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'phone_number']
