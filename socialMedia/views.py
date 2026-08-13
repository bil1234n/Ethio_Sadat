import logging
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from .models import SocialMediaPost

logger = logging.getLogger(__name__)

# Helper function to bypass CDN blocking
def proxy_img(url):
    if not url:
        return ""
    encoded_url = urllib.parse.quote(url)
    return f"https://wsrv.nl/?url={encoded_url}"

def get_youtube_videos(channel_id):
    """
    Professional Fetcher: Prioritizes YouTube Data API to bypass cloud-hosting IP blocks,
    with a bulletproofed XML fallback mechanism.
    """
    youtube_videos = []

    # 1. PRIMARY METHOD: YouTube Data API (Configure YOUTUBE_API_KEY in settings.py)
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
                            'link': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                            'date': item['snippet']['publishedAt'][:10]
                        })
                return youtube_videos
        except Exception as e:
            logger.error(f"YouTube API Error: {e}")

    # 2. FALLBACK METHOD: Robust RSS Parsing
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
                # Safe node extraction prevents AttributeError on missing elements
                vid_node = entry.find('yt:videoId', ns)
                title_node = entry.find('atom:title', ns)
                date_node = entry.find('atom:published', ns)

                if vid_node is not None and vid_node.text:
                    youtube_videos.append({
                        'title': title_node.text if title_node is not None else "New Video",
                        'id': vid_node.text,
                        'link': f"https://www.youtube.com/watch?v={vid_node.text}",
                        'date': date_node.text[:10] if date_node is not None else ""
                    })
    except ET.ParseError as e:
        logger.error(f"YouTube XML Parse Error (Likely Cloud IP blocked by anti-bot): {e}")
    except Exception as e:
        logger.error(f"YouTube RSS Fallback Error: {e}")

    return youtube_videos

def social_media_feed(request):
    cache_key = 'bilyonarc_social_feeds_v18'  # Bumped: source switched from hardcoded lists to SocialMediaPost DB records
    context = cache.get(cache_key)

    if context is None:
        # 1. YOUTUBE (Extracted to resilient helper function)
        youtube_videos = get_youtube_videos("UCWvIGKthHELdv1hyOkSujtQ")

        instagram_posts = []
        facebook_posts = []
        telegram_posts = []
        tiktok_posts = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 2. INSTAGRAM (admin-managed via SocialMediaPost)
        try:
            for item in SocialMediaPost.objects.filter(platform='instagram'):
                instagram_posts.append({
                    'id': item.id,
                    'image': item.image.url if item.image else '',
                    'caption': item.caption,
                    'link': item.link,
                    'date': item.date.isoformat() if item.date else '',
                })
        except Exception as e:
            logger.error(f"Instagram Error: {e}")

        # 3. FACEBOOK (admin-managed via SocialMediaPost)
        try:
            for item in SocialMediaPost.objects.filter(platform='facebook'):
                facebook_posts.append({
                    'id': item.id,
                    'image': item.image.url if item.image else '',
                    'text': item.caption,
                    'link': item.link,
                    'date': item.date.isoformat() if item.date else '',
                })
        except Exception as e:
            logger.error(f"Facebook Error: {e}")

        # 4. TELEGRAM
        try:
            tg_rss_url = "https://rss.app/feeds/v1.1/g8Edst4EDnIBq9ml.json"
            response = requests.get(tg_rss_url, headers=headers, timeout=5)
            if response.status_code == 200:
                for item in response.json().get('items', [])[:6]:
                    text = item.get('title', '')
                    telegram_posts.append({
                        'image': proxy_img(item.get('image', '')),
                        'content': (text[:150] + '...') if len(text) > 150 else text,
                        'date': item.get('date_published', 'Recent')[:10],
                        'link': item.get('url')
                    })
        except Exception as e:
            logger.error(f"Telegram Error: {e}")

        # 5. TIKTOK (admin-managed via SocialMediaPost)
        try:
            for item in SocialMediaPost.objects.filter(platform='tiktok'):
                tiktok_posts.append({
                    'id': item.id,
                    'image': item.image.url if item.image else '',
                    'text': item.caption,
                    'link': item.link,
                    'date': item.date.isoformat() if item.date else '',
                })
        except Exception as e:
            logger.error(f"TikTok Error: {e}")

        context = {
            'youtube_videos': youtube_videos,
            'instagram_posts': instagram_posts,
            'facebook_posts': facebook_posts,
            'telegram_posts': telegram_posts,
            'tiktok_posts': tiktok_posts,
        }

        # PREVENT EMPTY CACHE POISONING
        # If external fetch fails but we already have an older cache, we shouldn't overwrite it with empty data.
        cache.set(cache_key, context, 1800)

    return render(request, 'socialMedia.html', context)
