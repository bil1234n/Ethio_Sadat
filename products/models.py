from django.db import models
from django.core.validators import FileExtensionValidator
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Sofa', 'Sofa'),
        ('Mejlis', 'Mejlis'),
        ('Table', 'Table'),
        ('Bed', 'Bed'),
        ('Cabinet', 'Cabinet'),
        ('Side Drawer', 'Side Drawer'),
    ]

    # --- ADDED STATUS CHOICES ---
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Sofa')
    
    # --- ADDED STATUS FIELD ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    ar_model = models.FileField(
        upload_to='product_ar/', 
        null=True, 
        blank=True, 
        storage=RawMediaCloudinaryStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['glb', 'gltf', 'usdz'])],
        help_text="Upload a .glb file for the best 3D/AR web experience."
    ) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name