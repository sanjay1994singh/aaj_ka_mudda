from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from news.models import NewsArticle

from .forms import ReporterArticleForm, UserProfileForm


def can_manage_articles(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.role == "reporter" and user.is_verified


def user_articles_queryset(user):
    queryset = NewsArticle.objects.select_related("category", "author")
    if user.is_superuser or user.is_staff:
        return queryset
    return queryset.filter(author=user)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    articles = user_articles_queryset(request.user)
    own_articles = articles.filter(author=request.user)
    status_counts = dict(
        own_articles.values_list("status").annotate(total=Count("id"))
    )
    category_stats = own_articles.values("category__name").annotate(
        total=Count("id"),
        views=Sum("views"),
    ).order_by("-total")[:8]

    context = {
        "can_manage_articles": can_manage_articles(request.user),
        "total_articles": own_articles.count(),
        "published_articles": status_counts.get("published", 0),
        "draft_articles": status_counts.get("draft", 0),
        "total_views": own_articles.aggregate(total=Sum("views"))["total"] or 0,
        "breaking_articles": own_articles.filter(is_breaking=True).count(),
        "featured_articles": own_articles.filter(is_featured=True).count(),
        "latest_articles": own_articles.order_by("-created_at")[:10],
        "category_stats": category_stats,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
            current_user=request.user,
        )
        if form.is_valid():
            user = form.save(commit=False)
            if user.role != "reporter":
                user.is_verified = False
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user, current_user=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def article_create_view(request):
    if not can_manage_articles(request.user):
        messages.error(request, "Admin approval is required before you can add articles.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ReporterArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.created_at = timezone.now()
            article.save()
            messages.success(request, "Article created successfully.")
            return redirect("dashboard")
    else:
        form = ReporterArticleForm()

    return render(
        request,
        "accounts/article_form.html",
        {"form": form, "title": "Add Article"},
    )


@login_required
def article_update_view(request, pk):
    if not can_manage_articles(request.user):
        messages.error(request, "Admin approval is required before you can update articles.")
        return redirect("dashboard")

    article = get_object_or_404(user_articles_queryset(request.user), pk=pk)
    if request.method == "POST":
        form = ReporterArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article updated successfully.")
            return redirect("dashboard")
    else:
        form = ReporterArticleForm(instance=article)

    return render(
        request,
        "accounts/article_form.html",
        {"form": form, "title": "Update Article", "article": article},
    )


@login_required
def article_delete_view(request, pk):
    if not can_manage_articles(request.user):
        messages.error(request, "Admin approval is required before you can delete articles.")
        return redirect("dashboard")

    article = get_object_or_404(user_articles_queryset(request.user), pk=pk)
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted successfully.")
        return redirect("dashboard")

    return render(request, "accounts/article_confirm_delete.html", {"article": article})
