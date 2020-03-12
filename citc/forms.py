from django import forms
from django.core.exceptions import ValidationError


def validate_keys(value):
    if not value.startswith("http"):
        raise ValidationError("must be a URL")


class UserForm(forms.Form):
    uid = forms.CharField(label='uid', max_length=100)
    given_name = forms.CharField(label='Given name', max_length=100)
    sn = forms.CharField(label='Surname', max_length=100)
    keys = forms.CharField(label='SSH keys', help_text="A URL containing public SSH keys", validators=[validate_keys])
