from django.contrib import admin, messages

from .models import EpaperEdition, EpaperPage
from .services import convert_pdf_to_pages


class EpaperPageInline(admin.TabularInline):
    model = EpaperPage
    extra = 0
    readonly_fields = ("number", "image")


@admin.register(EpaperEdition)
class EpaperEditionAdmin(admin.ModelAdmin):
    list_display = ("city", "section", "publish_date", "created_at")
    list_filter = ("city", "section", "publish_date")
    search_fields = ("city", "section")
    readonly_fields = ("created_at",)
    inlines = (EpaperPageInline,)

    def save_model(self, request, obj, form, change):
        pdf_changed = not change or "pdf" in form.changed_data
        super().save_model(request, obj, form, change)

        if pdf_changed:
            try:
                page_count = convert_pdf_to_pages(obj)
            except RuntimeError as exc:
                self.message_user(request, str(exc), level=messages.ERROR)
            else:
                self.message_user(request, f"PDF converted successfully. {page_count} page(s) created.")


@admin.register(EpaperPage)
class EpaperPageAdmin(admin.ModelAdmin):
    list_display = ("edition", "number")
    list_filter = ("edition__city", "edition__section", "edition__publish_date")
