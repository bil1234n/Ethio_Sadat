from django.db import models
from django.core.validators import FileExtensionValidator
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import Notification
from django.urls import reverse

class Product(models.Model):
    # CHANGED: Moved from choices to a simple list of defaults
    DEFAULT_CATEGORIES = ['Sofa', 'Mejlis', 'Table', 'Bed', 'Cabinet', 'Side Drawer']

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]

    name = models.CharField(max_length=255)
    # CHANGED: Removed choices=... entirely to allow typing custom categories
    category = models.CharField(max_length=50, default='Mejlis')
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

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/gallery/')

    def __str__(self):
        return f"{self.product.name} - Gallery Image"

@receiver(post_save, sender=Product)
def notify_admin_new_product(sender, instance, created, **kwargs):
    if created:
        staff_users = User.objects.filter(is_staff=True)
        for admin in staff_users:
            Notification.objects.create(
                recipient=admin,
                title="New Product Added",
                message=f"A new product '{instance.name}' has been added to the catalog.",
                notification_type='Product',
                link=reverse('admin_product_manage')
            )

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"