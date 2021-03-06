from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from mgmt.users import user_exists


def validate_keys(value):
    try:
        URLValidator()(value)
    except ValidationError as e:
        if not (value.startswith("ssh-")):
            raise ValidationError("Must be a URL or an SSH public key")


def validate_user_not_exists(value):
    from mgmt.users import connection
    conn = connection()
    if user_exists(conn, value):
        raise ValidationError("User already exists")


class UserForm(forms.Form):
    uid = forms.CharField(label='uid', max_length=100, validators=[validate_user_not_exists])
    given_name = forms.CharField(label='Given name', max_length=100)
    sn = forms.CharField(label='Surname', max_length=100)
    keys = forms.CharField(label='SSH keys', help_text="An SSH public key or a URL containing public SSH keys", validators=[validate_keys])
