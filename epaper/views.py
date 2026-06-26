from io import BytesIO
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse

from .forms import EpaperEditionForm
from .models import EpaperEdition
from .services import convert_pdf_to_pages


SHARE_IMAGE_WIDTH = 1200
SHARE_IMAGE_HEIGHT = 630


def public_absolute_url(request, path):
    if not path:
        return ""
    parsed = urlparse(path)
    if parsed.scheme and parsed.netloc:
        return path
    site_url = getattr(settings, "SITE_URL", "").strip().rstrip("/")
    if site_url and "localhost" not in site_url and "127.0.0.1" not in site_url:
        return urljoin(f"{site_url}/", path.lstrip("/"))
    return request.build_absolute_uri(path)


def get_share_image_url(page):
    if not page or not page.image:
        return ""

    source_version = page.image.name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    share_path = f"epaper/share/{source_version}.jpg"
    if default_storage.exists(share_path):
        return default_storage.url(share_path)

    try:
        from PIL import Image

        with default_storage.open(page.image.name, "rb") as image_file:
            image = Image.open(image_file).convert("RGB")
            resampling_filter = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
            ratio = SHARE_IMAGE_WIDTH / image.width
            resized_height = max(1, round(image.height * ratio))
            image = image.resize((SHARE_IMAGE_WIDTH, resized_height), resampling_filter)

            if resized_height >= SHARE_IMAGE_HEIGHT:
                image = image.crop((0, 0, SHARE_IMAGE_WIDTH, SHARE_IMAGE_HEIGHT))
            else:
                canvas = Image.new("RGB", (SHARE_IMAGE_WIDTH, SHARE_IMAGE_HEIGHT), "white")
                canvas.paste(image, (0, (SHARE_IMAGE_HEIGHT - resized_height) // 2))
                image = canvas

            output = BytesIO()
            image.save(output, format="JPEG", quality=82, optimize=True, progressive=True)
            default_storage.save(share_path, ContentFile(output.getvalue()))
            return default_storage.url(share_path)
    except Exception:
        return page.image.url


def epaper_home(request, pk=None):
    edition = get_object_or_404(EpaperEdition, pk=pk) if pk else EpaperEdition.objects.first()
    edition_list = EpaperEdition.objects.all()
    page_records = list(edition.pages.all()) if edition else []
    pages = [
        {
            "number": page.number,
            "title": f"Page {page.number:02d}",
            "section": edition.section,
            "image": page.image.url,
        }
        for page in page_records
    ]
    editions_meta = [
        {
            "id": item.pk,
            "city": item.city,
            "section": item.section,
            "date": item.publish_date.isoformat(),
            "url": reverse("epaper:edition", kwargs={"pk": item.pk}),
        }
        for item in edition_list
    ]

    if edition:
        edition_date = edition.publish_date.strftime("%d %B %Y")
        seo_title = f"{edition.city} {edition.section} E-Paper - {edition_date}"
        seo_description = f"Read Aaj Ka Mudda {edition.city} {edition.section} e-paper for {edition_date}."
        current_date_iso = edition.publish_date.isoformat()
        current_city = edition.city
        current_section = edition.section
    else:
        edition_date = "No edition selected"
        seo_title = "E-Paper Reader | Aaj Ka Mudda"
        seo_description = "Read Aaj Ka Mudda e-paper online."
        current_date_iso = ""
        current_city = ""
        current_section = ""

    initial_page_record = page_records[0] if page_records else None
    canonical_url = public_absolute_url(request, request.path)
    share_image_url = get_share_image_url(initial_page_record) or static("images/share-fallback.jpg")
    absolute_image_url = public_absolute_url(request, share_image_url)
    share_version = edition.created_at.strftime("%Y%m%d%H%M%S") if edition else "latest"

    return render(
        request,
        "epaper/index.html",
        {
            "edition": edition,
            "edition_list": edition_list,
            "pages": pages,
            "edition_date": edition_date,
            "current_date_iso": current_date_iso,
            "current_city": current_city,
            "current_section": current_section,
            "editions_meta": editions_meta,
            "seo_title": seo_title,
            "seo_description": seo_description,
            "canonical_url": canonical_url,
            "whatsapp_share_url": f"{canonical_url}?share={share_version}",
            "absolute_image_url": absolute_image_url,
        },
    )


@staff_member_required
def upload_epaper(request):
    if request.method == "POST":
        form = EpaperEditionForm(request.POST, request.FILES)
        if form.is_valid():
            edition = form.save()
            try:
                page_count = convert_pdf_to_pages(edition)
            except RuntimeError as exc:
                messages.error(request, str(exc))
                return redirect("epaper:upload")
            messages.success(request, f"PDF uploaded and converted into {page_count} page(s).")
            return redirect("epaper:edition", pk=edition.pk)
    else:
        form = EpaperEditionForm()

    return render(request, "epaper/upload.html", {"form": form})
