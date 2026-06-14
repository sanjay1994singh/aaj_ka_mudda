from .models import Category

def categories_menu(request):

    categories = Category.objects.filter(
        show_on_menu=True
    ).order_by('id')

    return {
        'menu_categories': categories
    }