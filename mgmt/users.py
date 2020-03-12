import subprocess
import urllib.request
from copy import copy
from pathlib import Path

import yaml
from django.conf import settings
from ldap3 import Connection, ALL_ATTRIBUTES, MOCK_SYNC

BASE_DN = "ou=People,dc=citc,dc=acrc,dc=bristol,dc=ac,dc=uk"


def connection():
    if settings.IN_PRODUCTION:
        with open("/etc/citc/webui.yaml", "r") as f:
            config = yaml.safe_load(f)
        conn = Connection('ldap://localhost', user='cn=Directory Manager', password=config["ldap_password"], auto_bind=True)
    else:
        conn = Connection('my_fake_server', user='cn=Directory Manager', password='my_password', client_strategy=MOCK_SYNC)
        conn.bind()
    return conn


def get_all_users(conn, attributes=ALL_ATTRIBUTES):
    conn.search(BASE_DN, '(objectclass=posixAccount)', attributes=attributes)
    return copy(conn.entries)


def get_user(conn, uid, attributes=ALL_ATTRIBUTES):
    conn.search(BASE_DN, f'(&(objectclass=posixAccount)(cn={uid}))', attributes=attributes)
    try:
        return conn.entries[0]
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

    object_classes = [
        'top',
        'person',
        'organizationalPerson',
        'inetOrgPerson',
        'posixAccount',
    ]
    user_dict = {
        'cn': uid,
        'givenName': given_name,
        'sn': sn,
        'uid': uid,
        'uidNumber': uid_number,
        'gidNumber': gid_number,
        'homeDirectory': str(home_root / uid),
        'loginShell': '/bin/bash',
    }
    conn.add(f'cn={uid},{BASE_DN}', object_classes, user_dict)

    if keys.startswith("http"):
        with urllib.request.urlopen(keys) as f:
            keys = f.read()

    subprocess.run(["sudo", "/usr/local/libexec/create_home_dir", uid], check=True)
    subprocess.run(["sudo", "/usr/local/libexec/set_ssh_key", uid], check=True, input=keys)
