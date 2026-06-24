from django import forms

from news.models import NewsArticle

from .models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "avatar",
            "bio",
            "role",
            "facebook_url",
            "twitter_url",
            "instagram_url",
            "youtube_url",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)
        if not (current_user and (current_user.is_staff or current_user.is_superuser)):
            self.fields["role"].choices = (
                ("user", "User"),
                ("reporter", "Reporter"),
            )
        for field in self.fields.values():
            css_class = "form-control"
            if isinstance(field.widget, forms.Select):
                css_class = "form-select"
            field.widget.attrs["class"] = css_class


class ReporterArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = (
            "category",
            "title",
            "keywords",
            "short_description",
            "content",
            "image",
            "image_url",
            "image_description",
            "optional_url",
            "status",
            "is_breaking",
            "is_featured",
            "is_slider",
            "is_recommended",
        )
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 18}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif name == "content":
                existing_class = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing_class} form-control reporter-ckeditor article-content-input".strip()
                field.widget.attrs["rows"] = 18
            else:
                field.widget.attrs["class"] = "form-control"
