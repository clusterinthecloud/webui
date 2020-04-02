import pytest
import yaml
from django.urls import reverse


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
