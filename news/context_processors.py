# news/context_processors.py

from .models import NewsArticle


def breaking_news_processor(request):
    return {
        'breaking_news':
            NewsArticle.objects.filter(
                is_breaking=True,
                status='published'
            ).order_by('-created_at')[:10]
    }
