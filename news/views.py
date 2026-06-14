from news.models import NewsArticle
from category.models import Category
from django.shortcuts import render, get_object_or_404


def home(request):
    breaking_news = NewsArticle.objects.filter(
        is_breaking=True,
        status='published'
    )[:10]

    featured_news = NewsArticle.objects.filter(
        is_featured=True,
        status='published'
    )[:8]

    latest_news = NewsArticle.objects.filter(
        status='published'
    ).order_by('-created_at')[:20]

    categories = Category.objects.all()
    context = {
        'breaking_news': breaking_news,
        'featured_news': featured_news,
        'latest_news': latest_news,
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

    return render(
        request,
        'news_detail.html',
        {
            'news': news,
            'related_news': related_news,
            'latest_news': latest_news,
        }
    )
