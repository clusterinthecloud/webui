import secrets
import subprocess
import urllib.request
from pathlib import Path

import ldap3
import yaml
from django.conf import settings
from ldap3 import Connection, MOCK_SYNC, ObjectDef, Reader, Server, OFFLINE_DS389_1_3_3, Writer

BASE_DN = "ou=People,dc=citc,dc=acrc,dc=bristol,dc=ac,dc=uk"


def connection():
    if settings.IN_PRODUCTION:
        with open("/etc/citc/webui.yaml", "r") as f:
            config = yaml.safe_load(f)
        conn = Connection('ldap://localhost', user='cn=Directory Manager', password=config["ldap_password"], auto_bind=True)
    else:
        server = Server("my_fake_server", get_info=OFFLINE_DS389_1_3_3)
        conn = Connection(server, user='cn=Directory Manager', password='my_password', client_strategy=MOCK_SYNC, auto_bind=True)
    return conn


def get_all_users(conn, attributes=None):
    obj_posix_account = ObjectDef(['top', 'person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'], conn)
    r = Reader(conn, obj_posix_account, BASE_DN, attributes=attributes)
    r.search()
    return r


def get_user(conn, uid, attributes=None):
    obj_posix_account = ObjectDef(['top', 'person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'], conn)
    r = Reader(conn, obj_posix_account, BASE_DN, f"cn: {uid}", attributes=attributes)
    r.search()
    try:
        return r[0]
    except IndexError:
        raise LookupError("User not found")


def user_exists(conn, uid):
    try:
        get_user(conn, uid)
    except LookupError:
        return False
    else:
        return True


def create_user(conn: Connection, uid: str, given_name: str, sn: str, keys: str):
    # TODO make this repeatable and backoutable
    if user_exists(conn, uid):
        raise RuntimeError("User already exists")

    starting_uid_number = 10001
    gid_number = 100
    home_root = Path("/mnt/shared/home")
    uid_numbers = get_all_users(conn, attributes=["uidNumber"])
    try:
        max_uid = int(max(uid_numbers, key=lambda u: int(u.uidNumber.value)).uidNumber.value)
        uid_number = max_uid + 1
    except ValueError:
        uid_number = starting_uid_number

    password = secrets.token_urlsafe(30)

    obj_posix_account = ObjectDef(['top', 'person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'], conn)
    w = Writer(conn, obj_posix_account)
    e = w.new(f'cn={uid},{BASE_DN}')
    e.givenName = given_name
    e.sn = sn
    e.uid = uid
    e.uidNumber = uid_number
    e.gidNumber = gid_number
    e.homeDirectory = str(home_root / uid)
    e.loginShell = '/bin/bash'
    e.userPassword = ldap3.utils.hashed.hashed(ldap3.HASHED_SALTED_SHA512, password)
    w.commit()

    if keys.startswith("http"):
        with urllib.request.urlopen(keys) as f:
            keys = f.read()

    subprocess.run(["sudo", "/usr/local/libexec/create_home_dir", uid], check=True)
    subprocess.run(["sudo", "/usr/local/libexec/set_ssh_key", uid], check=True, input=keys)
    subprocess.run(["sudo", "/usr/local/libexec/set_password_file", uid], check=True, input=password)
