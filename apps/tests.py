import pytest
import yaml
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.models import App
from apps.views import get_app_state


@pytest.fixture(scope="function")
def auth_client(client, django_user_model):
    username = "citc"
    password = "bar"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client


@pytest.fixture
def app_info():
    return {
        "jupyterhub": yaml.safe_load("""
            name: JupyterHub
            description: A JupyterHub server with JupyterLab built-in
            icon: logo.svg
            variables:
              port:
                ansible_var: nginx_port
                default: 8002
                description: The port that JupyterHub will be available on
        """),
    }


def test_apps_index(auth_client, app_info, mocker):
    mocker.patch("apps.views.get_apps", lambda: app_info)
    r = auth_client.get(reverse('index'))
    assert "App Store" in r.content.decode()
    assert "JupyterHub" in r.content.decode()


@pytest.mark.django_db
def test_get_app_state(app_info):
    apps = get_app_state(app_info)
    assert apps["jupyterhub"]["state"] == "Not installed"

    App.objects.update_or_create(name="jupyterhub", defaults={"state": "P"})
    apps = get_app_state(app_info)
    assert apps["jupyterhub"]["state"] == "Installing"

    App.objects.update_or_create(name="jupyterhub", defaults={"state": "I"})
    apps = get_app_state(app_info)
    assert apps["jupyterhub"]["state"] == "Installed"


@pytest.mark.django_db
def test_start_app_install(auth_client, app_info, mocker):
    mocker.patch("apps.views.get_apps", lambda: app_info)

    apps = get_app_state(app_info)
    assert apps["jupyterhub"]["state"] == "Not installed"

    r = auth_client.post(reverse('app', kwargs={'name': 'jupyterhub'}), {"state": "installed"})
    assert list(get_messages(r.wsgi_request))
    message = list(get_messages(r.wsgi_request))[0].message
    assert message == "JupyterHub is being installed"

    r = auth_client.get(reverse('app', kwargs={'name': 'jupyterhub'}))
    assert r.json()["state"] == "Installing"
