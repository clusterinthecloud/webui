from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from citc.users import user_exists


def validate_keys(value):
    try:
        URLValidator()(value)
    except ValidationError as e:
        if not value.startswith("ssh-rsa"):
            raise ValidationError("Must be a URL or an SSH public key")


def validate_user_not_exists(value):
    from citc.users import connection
    conn = connection()
    if user_exists(conn, value):
        raise ValidationError("User already exists")


class UserForm(forms.Form):
    uid = forms.CharField(label='uid', max_length=100, validators=[validate_user_not_exists])
    given_name = forms.CharField(label='Given name', max_length=100)
    sn = forms.CharField(label='Surname', max_length=100)
    keys = forms.CharField(label='SSH keys', help_text="A URL containing public SSH keys", validators=[validate_keys])
