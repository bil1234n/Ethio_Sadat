from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # --- ADDED 'status' TO FIELDS ---
        fields = ['name', 'category', 'status', 'description', 'price', 'stock', 'image', 'ar_model']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}), 
            'status': forms.Select(attrs={'class': 'form-select'}), # <-- Added widget for status
        }