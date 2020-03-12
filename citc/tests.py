from citc.users import connection, get_all_users, create_user, get_user


def test_connection():
    conn = connection()
    users = get_all_users(conn)
    assert len(users) == 0


def test_create_user(mocker):
    mocker.patch('subprocess.run')
    conn = connection()
    create_user(conn, 'matt', 'Matt', 'Williams', "https://github.com/milliams.keys")
    users = get_all_users(conn)
    assert len(users) == 1
    assert users[0].sn == "Williams"
    assert users[0].uidNumber == "10001"


def test_create_user_get_uid(mocker):
    mocker.patch('subprocess.run')
    conn = connection()
    create_user(conn, 'matt1', 'Matt', 'Williams', "https://github.com/milliams.keys")
    create_user(conn, 'matt2', 'Matt', 'Williams', "https://github.com/milliams.keys")
    users = get_all_users(conn)
    assert len(users) == 2
    assert get_user(conn, "matt1").uidNumber == "10001"
    assert get_user(conn, "matt2").uidNumber == "10002"
