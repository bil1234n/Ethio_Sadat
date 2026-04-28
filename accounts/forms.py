from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os

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