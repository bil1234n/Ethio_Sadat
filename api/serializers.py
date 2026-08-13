from rest_framework import serializers
from products.models import Product, ProductImage, Wishlist
from django.contrib.auth.models import User
from accounts.models import UserProfile
from message.models import Feedback
from accounts.models import Notification
from accounts.models import SiteSettings
from socialMedia.models import SocialMediaPost

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # --- ADD THIS: Accept phone number from the app ---
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number'] # Add it to fields

    def create(self, validated_data):
        # Extract phone number before creating the User
        phone = validated_data.pop('phone_number', '')

        # 1. Securely create the user with hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        # 2. Automatically update the created UserProfile with the phone number
        if phone:
            phone = phone.replace(" ", "")
            if phone.startswith('0'):
                phone = phone[1:]
            if not phone.startswith('+251'):
                phone = f"+251{phone}"

            profile = user.profile
            profile.phone_number = phone
            profile.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    # ---> ADD THIS LINE TO GET ADMIN STATUS <---
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)

    class Meta:
        model = UserProfile
        # ---> ADD 'is_staff' TO FIELDS LIST <---
        fields =['username', 'email', 'company_name', 'phone_number', 'is_b2b_seller', 'created_at', 'is_staff']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        if 'email' in user_data:
            user.email = user_data['email']
            user.save()

        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        return instance

class FeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'username', 'name', 'email', 'phone', 'subject', 'message', 'admin_reply', 'is_replied', 'created_at']
        read_only_fields = ['admin_reply', 'is_replied']

class AdminReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['admin_reply', 'is_replied']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'link', 'is_read', 'created_at']


# --- 1. ADD THIS NEW SERIALIZER ---
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'status', 'description', 'price', 'stock', 'image', 'ar_model', 'images']

    # --- ADD THESE TWO METHODS TO HANDLE SAVING GALLERY IMAGES ---
    def create(self, validated_data):
        product = super().create(validated_data)
        # Fetch the array of gallery images sent from the app
        uploaded_images = self.context.get('request').FILES.getlist('uploaded_images')
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        product = super().update(instance, validated_data)
        uploaded_images = self.context.get('request').FILES.getlist('uploaded_images')
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']


# --- SOCIAL MEDIA MANAGEMENT (admin-managed posts, replaces hardcoded lists) ---
class SocialMediaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaPost
        fields = ['id', 'platform', 'link', 'image', 'caption', 'date', 'created_at']


# --- SITE SETTINGS (admin-editable app config, e.g. Telegram order username) ---
class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['telegram_order_username', 'updated_at']
        read_only_fields = ['updated_at']

    def validate_telegram_order_username(self, value):
        value = (value or '').strip().lstrip('@')
        if not value:
            raise serializers.ValidationError("Telegram username cannot be empty.")
        return value
