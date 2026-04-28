from django.db import models
from django.core.validators import FileExtensionValidator

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    # Added File Validator for Professional Security & Error handling
    ar_model = models.FileField(
        upload_to='product_ar/', 
        null=True, 
        blank=True, 
        validators=[FileExtensionValidator(allowed_extensions=['glb', 'gltf', 'usdz'])],
        help_text="Upload a .glb file for the best 3D/AR web experience."
    ) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name