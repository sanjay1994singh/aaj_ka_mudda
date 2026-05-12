from django.shortcuts import render, get_object_or_404
from .models import News, Category
from django.db.models import Q


def home(request):
    latest_news = News.objects.exclude(
        slug=''
    ).order_by('-created_at')[:10]

    breaking_news = News.objects.filter(is_breaking=True)[:5]

    trending_news = News.objects.filter(is_trending=True)[:6]

    categories = Category.objects.all()
    most_viewed_news = News.objects.order_by('-views')[:6]

    return render(request, 'home.html', {
        'latest_news': latest_news,
        'breaking_news': breaking_news,
        'trending_news': trending_news,
        'categories': categories,
        'most_viewed_news': most_viewed_news,
    })


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)

    news.views += 1
    news.save()

    related_news = News.objects.filter(
        category=news.category
    ).exclude(id=news.id)[:6]

    return render(request, 'news_detail.html', {
        'news': news,
        'related_news': related_news,
    })


def category_news(request, slug):
    category = get_object_or_404(Category, slug=slug)

    news = News.objects.filter(category=category)

    return render(request, 'category.html', {
        'category': category,
        'news': news,
    })


def search(request):
    query = request.GET.get('q')

    results = News.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query)
    )

    return render(request, 'search.html', {
        'results': results,
        'query': query
    })


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def privacy_policy(request):
    return render(request, 'privacy-policy.html')


def disclaimer(request):
    return render(request, 'disclaimer.html')


def terms(request):
    return render(request, 'terms.html')
