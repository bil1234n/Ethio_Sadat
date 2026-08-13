from django import forms
from .models import Product, ProductImage

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput
    
    def clean(self, data, initial=None):
        if not data or data == ['']:
            if self.required:
                raise forms.ValidationError("This field is required.")
            return []
            
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        else:
            return [single_file_clean(data, initial)]

class ProductForm(forms.ModelForm):
    additional_images = MultipleFileField(
        required=False,
        label="Additional Gallery Images (Select multiple files at once)",
        widget=MultipleFileInput(attrs={'class': 'form-control'})
    )
    
    clear_images = forms.BooleanField(
        required=False, 
        label="Clear existing additional images? (Check this to replace old gallery images)"
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'status', 'description', 'price', 'stock', 'image', 'additional_images', 'clear_images', 'ar_model']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            
            # UPDATE THIS LINE: Added autocomplete='off'
            'category': forms.TextInput(attrs={
                'list': 'category-list', 
                'placeholder': 'Select or Type...',
                'autocomplete': 'off' 
            }), 
            
            'status': forms.Select(attrs={'class': 'form-select'}),
        }