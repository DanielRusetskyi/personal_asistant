# chat/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupCreateForm(forms.Form):
    title = forms.CharField(label="Назва групи", max_length=200)


class GroupMembersForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        label="Учасники",
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 12, "class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        # не показуємо себе в списку (додамо власника автоматично)
        self.fields["members"].queryset = User.objects.exclude(id=user.id).order_by("username")
