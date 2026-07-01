from io import BytesIO
import re
from urllib.error import URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.views.decorators.cache import cache_control

from django.db.models import Q

from news.models import NewsArticle
from category.models import Category


YOUTUBE_CHANNEL_URL = 'https://www.youtube.com/@AajKaMudda'
YOUTUBE_SHORTS_URL = 'https://www.youtube.com/@AajKaMudda/shorts'
YOUTUBE_FEED_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
YOUTUBE_CACHE_SECONDS = 15 * 60


def public_absolute_url(path):
    return f"{settings.SITE_URL}{path}"


def request_absolute_url(request, path):
    return request.build_absolute_uri(path)


def share_description(news):
    source = news.short_description or strip_tags(news.content) or news.title or ''
    return Truncator(source.strip()).chars(155)


def article_image_url(request, news):
    if news.image_src:
        return request_absolute_url(request, news.image_src)
    return ''


def safe_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except UnicodeEncodeError:
        return len(text) * 24


def safe_draw_text(draw, position, text, font, fill):
    try:
        draw.text(position, text, font=font, fill=fill)
    except UnicodeEncodeError:
        draw.text(position, 'Read full story on Aaj Ka Mudda', font=font, fill=fill)


def category_latest_bundle(names, limit=4):
    category = Category.objects.filter(
        Q(name__in=names) | Q(slug__in=[name.lower().replace(' ', '-') for name in names])
    ).first()

    news_items = NewsArticle.objects.none()
    if category:
        news_items = NewsArticle.objects.filter(
            category=category,
            status='published',
        ).select_related('category').order_by('-created_at')[:limit]

    return {
        'category': category,
        'news': news_items,
    }


def fetch_url(url, timeout=5):
    request = Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AajKaMuddaBot/1.0)',
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode('utf-8', errors='ignore')


def get_youtube_channel_id():
    cache_key = 'youtube_channel_id:aaj-ka-mudda'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        html = fetch_url(YOUTUBE_CHANNEL_URL)
    except (OSError, URLError):
        return ''

    patterns = (
        r'"channelId":"(UC[^"]+)"',
        r'<meta itemprop="channelId" content="(UC[^"]+)">',
        r'"externalId":"(UC[^"]+)"',
    )
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            channel_id = match.group(1)
            cache.set(cache_key, channel_id, 24 * 60 * 60)
            return channel_id
    return ''


def latest_youtube_videos(limit=5):
    cache_key = f'youtube_latest_videos:aaj-ka-mudda:{limit}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    channel_id = get_youtube_channel_id()
    if not channel_id:
        cache.set(cache_key, [], 5 * 60)
        return []

    try:
        feed_xml = fetch_url(YOUTUBE_FEED_URL.format(channel_id=channel_id))
        root = ET.fromstring(feed_xml)
    except (OSError, URLError, ET.ParseError):
        cache.set(cache_key, [], 5 * 60)
        return []

    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'media': 'http://search.yahoo.com/mrss/',
        'yt': 'http://www.youtube.com/xml/schemas/2015',
    }
    videos = []
    for entry in root.findall('atom:entry', namespaces)[:limit]:
        video_id = entry.findtext('yt:videoId', default='', namespaces=namespaces)
        title = entry.findtext('atom:title', default='', namespaces=namespaces)
        published = entry.findtext('atom:published', default='', namespaces=namespaces)
        link_node = entry.find('atom:link[@rel="alternate"]', namespaces)
        link = link_node.attrib.get('href') if link_node is not None else ''
        thumbnail_node = entry.find('media:group/media:thumbnail', namespaces)
        thumbnail = thumbnail_node.attrib.get('url') if thumbnail_node is not None else ''

        if video_id and not thumbnail:
            thumbnail = f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'
        if video_id and not link:
            link = f'https://www.youtube.com/watch?v={video_id}'

        if title and link:
            videos.append({
                'title': title,
                'url': link,
                'thumbnail': thumbnail,
                'published': published,
            })

    cache.set(cache_key, videos, YOUTUBE_CACHE_SECONDS)
    return videos


def clean_youtube_text(value):
    return (
        value.replace('\\u0026', '&')
        .replace('&amp;', '&')
        .replace('\\"', '"')
        .strip()
    )


def latest_youtube_shorts(limit=5):
    cache_key = f'youtube_latest_shorts:aaj-ka-mudda:{limit}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        html = fetch_url(YOUTUBE_SHORTS_URL)
    except (OSError, URLError):
        cache.set(cache_key, [], 5 * 60)
        return []

    video_ids = []
    for pattern in (
        r'"reelWatchEndpoint":\{"videoId":"([^"]+)"',
        r'"webCommandMetadata":\{"url":"/shorts/([^"]+)"',
        r'"/shorts/([A-Za-z0-9_-]{8,})"',
    ):
        for video_id in re.findall(pattern, html):
            if video_id not in video_ids:
                video_ids.append(video_id)
            if len(video_ids) >= limit:
                break
        if len(video_ids) >= limit:
            break

    shorts = []
    for video_id in video_ids[:limit]:
        title = ''
        title_match = re.search(
            rf'"videoId":"{re.escape(video_id)}".{{0,1200}}?"title":\{{"runs":\[\{{"text":"([^"]+)"',
            html,
        )
        if not title_match:
            title_match = re.search(
                rf'"videoId":"{re.escape(video_id)}".{{0,1200}}?"accessibilityData":\{{"label":"([^"]+)"',
                html,
            )
        if title_match:
            title = clean_youtube_text(title_match.group(1))

        if not title:
            title = 'Aaj Ka Mudda Short Video'

        shorts.append({
            'title': title,
            'url': f'https://www.youtube.com/shorts/{video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
        })

    cache.set(cache_key, shorts, YOUTUBE_CACHE_SECONDS)
    return shorts


def home(request):
    breaking_news = NewsArticle.objects.filter(
        is_breaking=True,
        status='published'
    )[:10]

    latest_news = NewsArticle.objects.filter(
        status='published'
    ).order_by('-created_at')

    delhi_ncr = NewsArticle.objects.filter(
        status='published',
        category_id=2
    ).select_related(
        'category'
    ).order_by('-created_at')[:4]

    up_news = NewsArticle.objects.filter(
        status='published',
        category_id=3
    ).select_related(
        'category'
    ).order_by('-id')[:6]

    politics_news = NewsArticle.objects.filter(
        status='published',
        category_id=4
    ).select_related(
        'category'
    ).order_by('-created_at')[:4]

    national_bundle = category_latest_bundle(['National', 'राष्ट्रीय', 'Rashtriya'])
    article_bundle = category_latest_bundle(['Article', 'Artical', 'आर्टिकल'])
    lifestyle_bundle = category_latest_bundle(['Lifestyle', 'लाइफस्टाइल'])

    featured_news = latest_news.first()

    side_news = latest_news[1:5]

    categories = Category.objects.all()
    youtube_videos = latest_youtube_videos()
    youtube_shorts = latest_youtube_shorts()
    context = {
        'breaking_news': breaking_news,
        'featured_news': featured_news,
        'side_news': side_news,
        'latest_news': latest_news,
        'delhi_ncr': delhi_ncr,
        'up_news': up_news,
        'politics_news': politics_news,
        'national_bundle': national_bundle,
        'article_bundle': article_bundle,
        'lifestyle_bundle': lifestyle_bundle,
        'categories': categories,
        'youtube_videos': youtube_videos,
        'youtube_shorts': youtube_shorts,
    }

    return render(request, 'home.html', context)


def news_detail(request, slug):
    news = get_object_or_404(
        NewsArticle,
        slug=slug,
        status='published'
    )

    related_news = NewsArticle.objects.filter(
        category=news.category,
        status='published'
    ).exclude(id=news.id)[:6]

    latest_news = NewsArticle.objects.filter(
        status='published'
    ).exclude(id=news.id)[:6]

    canonical_path = reverse('news_detail', kwargs={'slug': news.slug})
    share_path = reverse('news_share_redirect', kwargs={'pk': news.pk})
    fallback_image_path = reverse('news_share_image', kwargs={'slug': news.slug})
    canonical_url = request_absolute_url(request, canonical_path)
    share_url = request_absolute_url(request, share_path)
    fallback_image_url = request_absolute_url(request, fallback_image_path)
    thumbnail_url = fallback_image_url
    description = share_description(news)
    share_text = f'{news.title} - {share_url}'

    return render(
        request,
        'news_detail.html',
        {
            'news': news,
            'related_news': related_news,
            'latest_news': latest_news,
            'canonical_url': canonical_url,
            'thumbnail_url': thumbnail_url,
            'share_url': share_url,
            'whatsapp_share_url': f'https://wa.me/?text={quote_plus(share_text)}',
            'facebook_share_url': (
                'https://www.facebook.com/sharer/sharer.php?'
                + urlencode({'u': share_url})
            ),
            'x_share_url': (
                'https://twitter.com/intent/tweet?'
                + urlencode({'url': share_url, 'text': news.title})
            ),
            'copy_share_url': share_url,
            'meta_description': description,
        }
    )


def news_share_redirect(request, pk):
    news = get_object_or_404(
        NewsArticle,
        pk=pk,
        status='published'
    )
    return redirect('news_detail', slug=news.slug, permanent=True)


@cache_control(public=True, max_age=86400)
def news_share_image(request, slug):
    news = get_object_or_404(
        NewsArticle,
        slug=slug,
        status='published'
    )

    canvas_size = (1200, 630)
    image = None
    has_article_image = False

    local_image_path = news.local_image_path()
    if local_image_path and local_image_path.exists():
        try:
            with local_image_path.open('rb') as image_file:
                image = Image.open(image_file).convert('RGB')
                image = ImageOps.fit(image, canvas_size, method=Image.Resampling.LANCZOS)
                has_article_image = True
        except Exception:
            image = None

    if image is None:
        image = Image.new('RGB', canvas_size, '#0b1f3a')
        draw = ImageDraw.Draw(image)
        for y in range(canvas_size[1]):
            red = 11 + int(y * 0.10)
            green = 31 + int(y * 0.04)
            blue = 58 + int(y * 0.02)
            draw.line([(0, y), (canvas_size[0], y)], fill=(red, green, blue))

    if not has_article_image:
        overlay = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle((0, 400, 1200, 630), fill=(0, 0, 0, 160))
        image = Image.alpha_composite(image.convert('RGBA'), overlay)

        draw = ImageDraw.Draw(image)
        try:
            title_font = ImageFont.truetype('arial.ttf', 48)
            brand_font = ImageFont.truetype('arial.ttf', 32)
        except OSError:
            title_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()

        draw.text((48, 420), 'Aaj Ka Mudda', font=brand_font, fill='#ffffff')
        title = news.title[:110]
        lines = []
        words = title.split()
        current_line = ''
        for word in words:
            test_line = f'{current_line} {word}'.strip()
            if safe_text_width(draw, test_line, title_font) <= 1080:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
            if len(lines) == 2:
                break
        if current_line and len(lines) < 3:
            lines.append(current_line)

        y = 465
        for line in lines[:3]:
            safe_draw_text(draw, (48, y), line, title_font, '#ffffff')
            y += 52

    output = BytesIO()
    image.convert('RGB').save(output, format='JPEG', quality=82, optimize=True, progressive=True)
    return HttpResponse(output.getvalue(), content_type='image/jpeg')
