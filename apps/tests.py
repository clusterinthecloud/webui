from pathlib import Path

import pytest
from django.http import HttpResponse
from django.urls import reverse


@pytest.fixture(scope="function")
def auth_client(client, django_user_model):
    username = "citc"
    password = "bar"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client


def test_apps_index(auth_client, mocker):
    mocker.patch("apps.views.get_apps", lambda: {})
    r = auth_client.get(reverse('index'))
    assert "App Store" in r.content.decode()
