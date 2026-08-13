# api/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    api_root, RegisterAPIView, UserProfileAPIView,
    ProductListCreateAPIView, ProductDetailAPIView,
    FeedbackListCreateAPIView, AdminFeedbackListAPIView, AdminFeedbackReplyAPIView,
    SocialMediaAPIView, NotificationListAPIView, NotificationReadAPIView,
    MobileGoogleLoginAPIView,
    # --- SOCIAL MEDIA POST MANAGEMENT (admin CRUD) ---
    SocialMediaPostListCreateAPIView, SocialMediaPostDetailAPIView,
    # --- SITE SETTINGS (admin-editable Telegram order username, etc.) ---
    SiteSettingsAPIView,
    # --- IMPORT THE NEW VIEWS ---
    WishlistAPIView, WishlistToggleAPIView, WishlistCheckAPIView # <-- Import the new view
)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('profile/', UserProfileAPIView.as_view(), name='api_profile'),

    # --- GOOGLE MOBILE API ENDPOINT ---
    path('auth/google/', MobileGoogleLoginAPIView.as_view(), name='api_google_login'),

    # --- UPDATED PRODUCT API ENDPOINTS ---
    path('products/', ProductListCreateAPIView.as_view(), name='api_product_list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('feedbacks/', FeedbackListCreateAPIView.as_view(), name='api_feedbacks'),
    path('admin/feedbacks/', AdminFeedbackListAPIView.as_view(), name='api_admin_feedbacks'),
    path('admin/feedbacks/<int:pk>/reply/', AdminFeedbackReplyAPIView.as_view(), name='api_admin_feedbacks_reply'),

    path('social-media/', SocialMediaAPIView.as_view(), name='api_social_media'),

    # --- SOCIAL MEDIA MANAGEMENT (admin CRUD: link, image, caption, date) ---
    path('social-media/posts/', SocialMediaPostListCreateAPIView.as_view(), name='api_social_media_posts'),
    path('social-media/posts/<int:pk>/', SocialMediaPostDetailAPIView.as_view(), name='api_social_media_post_detail'),

    # --- SITE SETTINGS (e.g. Telegram order username used by the "Order on Telegram" button) ---
    path('settings/', SiteSettingsAPIView.as_view(), name='api_site_settings'),

    path('notifications/', NotificationListAPIView.as_view(), name='api_notifications'),
    path('notifications/<int:pk>/read/', NotificationReadAPIView.as_view(), name='api_notifications_read'),

    # --- ADD THESE WISHLIST API ENDPOINTS ---
    path('wishlist/', WishlistAPIView.as_view(), name='api_wishlist'),
    path('wishlist/toggle/<int:product_id>/', WishlistToggleAPIView.as_view(), name='api_wishlist_toggle'),
    path('wishlist/check/<int:product_id>/', WishlistCheckAPIView.as_view(), name='api_wishlist_check'),
]
