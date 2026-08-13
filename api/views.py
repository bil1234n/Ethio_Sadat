from rest_framework import generics
from products.models import Product, Wishlist
from .serializers import ProductSerializer, WishlistSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from accounts.models import UserProfile
from .serializers import ProfileSerializer
from message.models import Feedback
from .serializers import FeedbackSerializer, AdminReplySerializer
from django.shortcuts import render, redirect, get_object_or_404
import uuid
import requests
from django.conf import settings
from django.urls import reverse
import urllib.parse
import logging
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from accounts.models import Notification
from .serializers import NotificationSerializer
from socialMedia.models import SocialMediaPost
from .serializers import SocialMediaPostSerializer
from accounts.models import SiteSettings
from .serializers import SiteSettingsSerializer

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
import sys
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Welcome to the B2B Hub API",
        "endpoints": {
            "products": "/api/products/",
            "auth_token": "/api/token/",
            "token_refresh": "/api/token/refresh/"
        }
    })

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Account created successfully. You can now log in."},
                status=status.HTTP_201_CREATED
            )
        # Return exactly what went wrong (e.g. username already taken)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated] # Only logged in users can access!

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully!", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 1. Handles GET (All users) and POST (Admins only)
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()] # Only Admins can add products
        return[] # Anyone can view products

# 2. Handles PUT and DELETE (Admins only)
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes =[IsAdminUser] # Only admins can edit or delete

# USER: Get own messages & Create new message
class FeedbackListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ADMIN: List all messages
class AdminFeedbackListAPIView(generics.ListAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUser]
    queryset = Feedback.objects.all().order_by('is_replied', '-created_at')

# ADMIN: Reply to a message
class AdminFeedbackReplyAPIView(generics.UpdateAPIView):
    serializer_class = AdminReplySerializer
    permission_classes = [IsAdminUser]
    queryset = Feedback.objects.all()

    def perform_update(self, serializer):
        serializer.save(is_replied=True)


# Helper function to bypass CDN blocking
def proxy_img(url):
    if not url:
        return ""
    encoded_url = urllib.parse.quote(url)
    return f"https://wsrv.nl/?url={encoded_url}"

def get_youtube_videos_api(channel_id):
    """
    Resilient YouTube Fetcher for DRF:
    Attempts YouTube Data API v3 first, falls back to safe XML parsing.
    """
    youtube_videos = []

    # 1. PRIMARY METHOD: YouTube Data API (Requires YOUTUBE_API_KEY in settings.py)
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if api_key:
        try:
            api_url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=6"
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                for item in response.json().get('items', []):
                    if item['id'].get('kind') == 'youtube#video':
                        youtube_videos.append({
                            'title': item['snippet']['title'],
                            'id': item['id']['videoId'],
                            'date': item['snippet']['publishedAt'][:10],
                            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                        })
                return youtube_videos
        except Exception as e:
            logger.error(f"YouTube API Error: {e}")

    # 2. FALLBACK METHOD: Safe XML Parsing
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/atom+xml,application/xml,text/xml,*/*;q=0.9'
    }
    try:
        yt_feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        response = requests.get(yt_feed_url, headers=headers, timeout=7)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

            for entry in root.findall('atom:entry', ns)[:6]:
                vid_node = entry.find('yt:videoId', ns)
                title_node = entry.find('atom:title', ns)
                date_node = entry.find('atom:published', ns)

                if vid_node is not None and vid_node.text:
                    youtube_videos.append({
                        'title': title_node.text if title_node is not None else "New Video",
                        'id': vid_node.text,
                        'date': date_node.text[:10] if date_node is not None else "",
                        'url': f"https://www.youtube.com/watch?v={vid_node.text}"
                    })
    except ET.ParseError as e:
        logger.error(f"YouTube XML Parse Error: {e}")
    except Exception as e:
        logger.error(f"YouTube RSS Fallback Error: {e}")

    return youtube_videos


class SocialMediaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Bumped version: instagram/facebook/tiktok now come from the admin-managed
        # SocialMediaPost model instead of hardcoded lists. Cache is also flushed
        # automatically whenever a post is created/edited/deleted (see socialMedia/models.py).
        cache_key = 'rn_social_feeds_api_v5'
        data = cache.get(cache_key)

        if data is None:
            # 1. YOUTUBE (Using resilient helper)
            youtube_data = get_youtube_videos_api("UCWvIGKthHELdv1hyOkSujtQ")

            data = {
                "youtube": youtube_data,
                "instagram": [],
                "facebook": [],
                "telegram": [],
                "tiktok": []
            }
            headers = {'User-Agent': 'Mozilla/5.0'}

            # 2. INSTAGRAM (admin-managed via SocialMediaPost)
            try:
                for item in SocialMediaPost.objects.filter(platform='instagram'):
                    data["instagram"].append({
                        'id': item.id,
                        'image': item.image.url if item.image else '',
                        'text': item.caption,
                        'link': item.link,
                        'date': item.date.isoformat() if item.date else '',
                    })
            except Exception as e:
                logger.error(f"IG Error: {e}")

            # 3. FACEBOOK (admin-managed via SocialMediaPost)
            try:
                for item in SocialMediaPost.objects.filter(platform='facebook'):
                    data["facebook"].append({
                        'id': item.id,
                        'image': item.image.url if item.image else '',
                        'text': item.caption,
                        'link': item.link,
                        'date': item.date.isoformat() if item.date else '',
                    })
            except Exception as e:
                logger.error(f"FB Error: {e}")

            # 4. TELEGRAM
            try:
                res = requests.get("https://rss.app/feeds/v1.1/g8Edst4EDnIBq9ml.json", headers=headers, timeout=5)
                if res.status_code == 200:
                    for item in res.json().get('items', [])[:6]:
                        text = item.get('title', '')
                        data["telegram"].append({
                            'image': proxy_img(item.get('image', '')),
                            'text': (text[:150] + '...') if len(text) > 150 else text,
                            'link': item.get('url'),
                            'date': item.get('date_published', 'Recent')[:10]
                        })
            except Exception as e:
                logger.error(f"TG Error: {e}")

            # 5. TIKTOK (admin-managed via SocialMediaPost)
            try:
                for item in SocialMediaPost.objects.filter(platform='tiktok'):
                    data["tiktok"].append({
                        'id': item.id,
                        'image': item.image.url if item.image else '',
                        'text': item.caption,
                        'link': item.link,
                        'date': item.date.isoformat() if item.date else '',
                    })
            except Exception as e:
                logger.error(f"TK Error: {e}")

            # Cache the successfully built JSON payload
            cache.set(cache_key, data, 1800)

        return Response(data)


# --- SOCIAL MEDIA MANAGEMENT (admin CRUD, mirrors the Product admin pattern) ---
class SocialMediaPostListCreateAPIView(generics.ListCreateAPIView):
    """Handles GET (anyone) and POST (admins only) for social media posts."""
    serializer_class = SocialMediaPostSerializer

    def get_queryset(self):
        queryset = SocialMediaPost.objects.all()
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)
        return queryset

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return []


class SocialMediaPostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Handles GET/PUT/PATCH/DELETE for a single social media post (admins only for writes)."""
    queryset = SocialMediaPost.objects.all()
    serializer_class = SocialMediaPostSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAdminUser()]


# --- SITE SETTINGS (admin-editable app config) ---
class SiteSettingsAPIView(APIView):
    """
    GET: anyone can read current settings (e.g. the mobile app needs the
    Telegram order username to build the "Order on Telegram" link).
    PUT/PATCH: admins only, used by the Inventory page's settings form.
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        settings_obj = SiteSettings.load()
        return Response(SiteSettingsSerializer(settings_obj).data)

    def put(self, request):
        settings_obj = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


# Fetch all notifications for the logged-in user
class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

# Mark a specific notification as read
class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

class MobileGoogleLoginAPIView(APIView):
    """
    API endpoint for handling Google Sign-In from the Mobile App.
    Accepts an `id_token`, validates it, creates/retrieves the user, and returns JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({"error": "No ID token provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ✅ FIX — verify without audience enforcement, then check manually
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            VALID_CLIENT_IDS = [
                settings.GOOGLE_WEB_CLIENT_ID,
                settings.GOOGLE_ANDROID_CLIENT_ID,  # add both to settings.py
            ]
            if idinfo.get('aud') not in VALID_CLIENT_IDS:
                return Response({"error": "Invalid token audience."}, status=status.HTTP_401_UNAUTHORIZED)

            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            if not email:
                return Response({"error": "No email address associated with this Google account."}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Match or Create the user (reusing your accounts/views.py logic)
            user = User.objects.filter(email__iexact=email).first()

            if not user:
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create(
                    username=username,
                    email=email.lower(),
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_unusable_password()
                user.save()

            # 3. Generate JWT Tokens for the mobile app session
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"Mobile Google Auth Error: {e}")
            return Response({"error": "Invalid Google token provided."}, status=status.HTTP_401_UNAUTHORIZED)


class WishlistAPIView(generics.ListAPIView):
    """Returns all wishlisted products for the logged-in mobile user"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).order_by('-added_at')


class WishlistToggleAPIView(APIView):
    """Toggles a product in/out of the user's wishlist"""
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if not created:
            wishlist_item.delete()
            return Response({'status': 'removed', 'is_wishlisted': False}, status=status.HTTP_200_OK)

        return Response({'status': 'added', 'is_wishlisted': True}, status=status.HTTP_201_CREATED)


class WishlistCheckAPIView(APIView):
    """Checks if a specific product is in the user's wishlist"""
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        is_wishlisted = Wishlist.objects.filter(user=request.user, product_id=product_id).exists()
        return Response({'is_wishlisted': is_wishlisted}, status=status.HTTP_200_OK)
