from django import forms

from .models import EpaperEdition


class EpaperEditionForm(forms.ModelForm):
    class Meta:
        model = EpaperEdition
        fields = ("city", "section", "publish_date", "pdf")
        widgets = {
            "publish_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
