import pytest
from django.urls import reverse

from citc.users import connection, get_all_users, create_user, get_user


@pytest.fixture(scope="function")
def auth_client(client, django_user_model):
    username = "citc"
    password = "bar"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client


@pytest.fixture(scope="function")
def conn():
    return connection()


def test_connection(conn):
    users = get_all_users(conn)
    assert len(users) == 0


def test_create_user(conn, mocker):
    mocker.patch('subprocess.run')
    create_user(conn, 'matt', 'Matt', 'Williams', "https://github.com/milliams.keys")
    users = get_all_users(conn)
    assert len(users) == 1
    assert users[0].sn == "Williams"
    assert users[0].uidNumber == "10001"


def test_get_user(conn):
    with pytest.raises(LookupError):
        get_user(conn, "matt")


def test_duplicate_user(conn, mocker):
    mocker.patch('subprocess.run')
    create_user(conn, 'matt', "", "", "")
    with pytest.raises(RuntimeError):
        create_user(conn, 'matt', "", "", "")


def test_create_user_get_uid(conn, mocker):
    mocker.patch('subprocess.run')
    create_user(conn, 'matt1', 'Matt', 'Williams', "https://github.com/milliams.keys")
    create_user(conn, 'matt2', 'Matt', 'Williams', "https://github.com/milliams.keys")
    users = get_all_users(conn)
    assert len(users) == 2
    assert get_user(conn, "matt1").uidNumber == "10001"
    assert get_user(conn, "matt2").uidNumber == "10002"


def test_form_validate(auth_client, mocker):
    m = mocker.patch("citc.users.user_exists")
    auth_client.post(reverse('add_user'), {"uid": "foo", "given_name": "foo", "sn": "foo", "keys": "http://foo"})
    assert m.called_once_with("foo", "foo", "foo", "http://foo")
