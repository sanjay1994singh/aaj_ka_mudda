from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import cache_control

from news.models import NewsArticle
from category.models import Category


def public_absolute_url(path):
    return f"{settings.SITE_URL}{path}"


def share_description(news):
    return (news.short_description or news.title or '').strip()[:180]


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

    featured_news = latest_news.first()

    side_news = latest_news[1:5]

    categories = Category.objects.all()
    context = {
        'breaking_news': breaking_news,
        'featured_news': featured_news,
        'side_news': side_news,
        'latest_news': latest_news,
        'delhi_ncr': delhi_ncr,
        'up_news': up_news,
        'politics_news': politics_news,
        'categories': categories,
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

    article_path = reverse('news_detail', kwargs={'slug': news.slug})
    share_image_path = reverse('news_share_image', kwargs={'slug': news.slug})
    share_url = public_absolute_url(article_path)
    share_image_url = public_absolute_url(share_image_path)
    description = share_description(news)

    return render(
        request,
        'news_detail.html',
        {
            'news': news,
            'related_news': related_news,
            'latest_news': latest_news,
            'share_url': share_url,
            'share_text': f'{news.title} {share_url}',
            'share_image_url': share_image_url,
            'meta_description': description,
        }
    )


@cache_control(public=True, max_age=86400)
def news_share_image(request, slug):
    news = get_object_or_404(
        NewsArticle,
        slug=slug,
        status='published'
    )

    canvas_size = (1200, 630)
    image = None

    if news.image:
        try:
            with news.image.open('rb') as image_file:
                image = Image.open(image_file).convert('RGB')
                image = ImageOps.fit(image, canvas_size, method=Image.Resampling.LANCZOS)
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
    image.convert('RGB').save(output, format='JPEG', quality=88, optimize=True)
    return HttpResponse(output.getvalue(), content_type='image/jpeg')
