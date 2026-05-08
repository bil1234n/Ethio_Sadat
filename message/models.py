from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    
    # --- ADDED FIELDS ---
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    # --------------------
    
    subject = models.CharField(max_length=200)
    message = models.TextField(help_text="Write your feedback or issue here.")
    
    # Admin Response Fields
    admin_reply = models.TextField(blank=True, null=True, help_text="Admin's response will appear here.")
    is_replied = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.name}" # Changed to show the user's name

    class Meta:
        ordering = ['-created_at'] # Shows newest messages first