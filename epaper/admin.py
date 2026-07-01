from django.contrib import admin, messages

from .models import EpaperEdition, EpaperPage, EpaperRegion
from .services import convert_pdf_to_pages


class EpaperPageInline(admin.TabularInline):
    model = EpaperPage
    extra = 0
    readonly_fields = ("number", "image")


@admin.register(EpaperRegion)
class EpaperRegionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)


@admin.register(EpaperEdition)
class EpaperEditionAdmin(admin.ModelAdmin):
    list_display = ("city", "region", "section", "publish_date", "created_at")
    list_filter = ("region", "city", "section", "publish_date")
    search_fields = ("city", "region__name", "section")
    readonly_fields = ("created_at",)
    inlines = (EpaperPageInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            kwargs["queryset"] = EpaperRegion.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        pdf_changed = not change or "pdf" in form.changed_data
        if obj.region:
            obj.city = obj.region.name
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
