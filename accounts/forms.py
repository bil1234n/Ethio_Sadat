# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os
from .models import UserProfile

# --- Form to handle the UserProfile part of registration ---
class UserProfileRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number'] 
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '911 234 567'})
        }
        help_texts = {
            'phone_number': 'Optional: Enter your local phone number.'
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone = phone.replace(" ", "")
            if phone.startswith('0'):
                phone = phone[1:]
            if not phone.startswith('+251'):
                phone = f"+251{phone}"
        return phone


# --- Custom Form for Standard User Registration ---
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        # REMOVED: 'first_name' and 'last_name' from fields array
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        """Enforces case-insensitive uniqueness and lowercases the input string"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError("An account with this email address already exists.")
        return email


# --- Admin Registration Form ---
class AdminRegistrationForm(UserCreationForm):
    passcode = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Secret Passcode'}),
        required=True,
        help_text="Requires authorization passcode."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError("An account with this email address already exists.")
        return email

    def clean_passcode(self):
        passcode = self.cleaned_data.get('passcode')
        correct_passcode = os.environ.get('ADMIN_REGISTER_PASSCODE')
        if not correct_passcode:
            raise ValidationError("Server configuration error: Passcode not set in .env")
        if passcode != correct_passcode:
            raise ValidationError("Invalid Admin Passcode! Access Denied.")
        return passcode
    

# --- User Model Update Form ---
class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        disabled=True, 
        help_text="Your username cannot be changed."
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This email address is already in use by another account.")
        return email


# --- User Profile Model Update Form ---
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'phone_number']

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone = phone.replace(" ", "")
            if phone.startswith('0'):
                phone = phone[1:]
            if not phone.startswith('+251'):
                phone = f"+251{phone}"
        return phone