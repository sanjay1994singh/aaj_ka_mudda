from django.shortcuts import render, get_object_or_404
from .models import Category
from news.models import NewsArticle


def category_news(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug
    )

    news_list = NewsArticle.objects.filter(
        category=category,
        status='published'
    ).order_by('-created_at')

    featured_news = news_list.first()
    other_news = news_list[1:13]

    return render(request, 'category_news.html', {
        'category': category,
        'featured_news': featured_news,
        'other_news': other_news,
        'news_list': news_list,
    })
