import logging
import requests
import urllib.parse
from django.shortcuts import render
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Helper function to bypass Instagram/Facebook CDN blocking
def proxy_img(url):
    if not url:
        return ""
    # We use wsrv.nl to proxy the image, stripping hotlink protections
    encoded_url = urllib.parse.quote(url)
    return f"https://wsrv.nl/?url={encoded_url}"

def social_media_feed(request):
    # Bumped cache to v11 to force new proxied URLs to load
    cache_key = 'bilyonarc_social_feeds_v11' 
    context = cache.get(cache_key)

    if context is None:
        youtube_videos = []
        instagram_posts = []
        facebook_posts = []
        telegram_posts = []
        tiktok_posts = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 1. YOUTUBE
        try:
            yt_rss_url = "https://rss.app/feeds/v1.1/cpCdxlHdjRkWqno7.json"
            response = requests.get(yt_rss_url, headers=headers, timeout=5)
            if response.status_code == 200:
                for item in response.json().get('items', [])[:6]:
                    video_url = item.get('url', '')
                    video_id = None
                    if 'v=' in video_url:
                        video_id = video_url.split('v=')[-1].split('&')[0]
                    elif 'youtu.be/' in video_url:
                        video_id = video_url.split('/')[-1]

                    if video_id:
                        youtube_videos.append({
                            'title': item.get('title', 'YouTube Video'),
                            'id': video_id,
                            'date': item.get('date_published', '')[:10]
                        })
        except Exception as e:
            logger.error(f"YouTube Error: {e}")
                
        # 2. INSTAGRAM (Proxied)
        try:
            ig_rss_url = "https://rss.app/feeds/v1.1/mRwix7Jny8EcTv4b.json"
            response = requests.get(ig_rss_url, headers=headers, timeout=5)
            if response.status_code == 200:
                for item in response.json().get('items', [])[:6]:
                    img_url = item.get('image', '')
                    attachments = item.get('attachments', [])
                    if attachments and isinstance(attachments, list):
                        img_url = attachments[0].get('url', img_url)

                    caption = item.get('title', '')
                    instagram_posts.append({
                        'image': proxy_img(img_url), # APPLIED PROXY HERE
                        'caption': (caption[:120] + '...') if len(caption) > 120 else caption,
                        'link': item.get('url'),
                        'date': item.get('date_published', 'Recent')[:10]
                    })
        except Exception as e:
            logger.error(f"Instagram Error: {e}")

        # 3. FACEBOOK (Proxied)
        try:
            fb_rss_url = "https://rss.app/feeds/v1.1/8YMeWLzHW2xSczZa.json"
            response = requests.get(fb_rss_url, headers=headers, timeout=5)
            if response.status_code == 200:
                for item in response.json().get('items', [])[:6]:
                    img_url = item.get('image', '')
                    attachments = item.get('attachments', [])
                    if attachments and isinstance(attachments, list):
                        img_url = attachments[0].get('url', img_url)

                    text = item.get('title', '')
                    facebook_posts.append({
                        'image': proxy_img(img_url), # APPLIED PROXY HERE
                        'text': (text[:120] + '...') if len(text) > 120 else text,
                        'link': item.get('url'),
                        'date': item.get('date_published', 'Recent')[:10]
                    })
        except Exception as e:
            logger.error(f"Facebook Error: {e}")

        # 4. TELEGRAM
        try:
            tg_rss_url = "https://rss.app/feeds/v1.1/C8098HQewaPWEOJZ.json"
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

        # 5. TIKTOK (Proxied)
        try:
            tk_rss_url = "https://rss.app/feeds/v1.1/4bdQLU8ATin59vCf.json"
            response = requests.get(tk_rss_url, headers=headers, timeout=5)
            if response.status_code == 200:
                for item in response.json().get('items', [])[:6]:
                    text = item.get('title', '')
                    tiktok_posts.append({
                        'image': proxy_img(item.get('image', '')), # APPLIED PROXY HERE
                        'text': (text[:100] + '...') if len(text) > 100 else text,
                        'link': item.get('url')
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
        
        cache.set(cache_key, context, 1800) # 30 mins

    return render(request, 'socialMedia.html', context)