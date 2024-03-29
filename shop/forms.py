from django import forms
from django.forms import RadioSelect

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("user", "rating", "review")
        widgets = {
            "user": forms.TextInput(
                attrs={
                    "type": "text",
                    "class": "form-control",
                    "id": "user",
                    "aria-describedby": "userHelp",
                    "placeholder": "Пользователь",
                    "name": "user",
                    "data-cip-id": "user",
                }
            ),
            "rating": RadioSelect(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
            ),
            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "id": "content",
                    "placeholder": "Содержание",
                    "name": "description",
                }
            ),
        }
