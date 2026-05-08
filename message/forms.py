from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        # ADDED THE NEW FIELDS HERE:
        fields = ['name', 'email', 'phone', 'subject', 'message'] 
        widgets = {
            # ADDED NEW WIDGETS:
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone Number'}),
            
            # YOUR ORIGINAL WIDGETS:
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What is this regarding?'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message here...'}),
        }

class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['admin_reply']
        widgets = {
            'admin_reply': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Type your reply to the user here...'
            }),
        }