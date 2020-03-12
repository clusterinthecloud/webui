from copy import copy
from pathlib import Path

import yaml
from django.conf import settings
from ldap3 import Server, Connection, ALL_ATTRIBUTES, MOCK_SYNC

BASE_DN = "ou=People,dc=citc,dc=acrc,dc=bristol,dc=ac,dc=uk"


def connection():
    if settings.IN_PRODUCTION:
        with open("/etc/citc/webui.yaml", "r") as f:
            config = yaml.safe_load(f)
        conn = Connection('ldap://localhost', user='cn=Directory Manager', password=config["ldap_password"], auto_bind=True)
    else:
        server = Server('my_fake_server')
        conn = Connection(server, user='cn=Directory Manager', password='my_password', client_strategy=MOCK_SYNC)
        conn.bind()
    return conn


def get_all_users(conn, attributes=ALL_ATTRIBUTES):
    conn.search(BASE_DN, '(objectclass=posixAccount)', attributes=attributes)
    return copy(conn.entries)


def get_user(conn, uid, attributes=ALL_ATTRIBUTES):
    conn.search(BASE_DN, f'(&(objectclass=posixAccount)(cn={uid}))', attributes=attributes)
    return conn.entries[0]


def create_user(conn, uid, given_name, sn, keys):
    starting_uid_number = 10001
    gid_number = 100
    home_root = Path("/mnt/shared/home")
    uid_numbers = get_all_users(conn, attributes=["uidNumber"])
    try:
        max_uid = int(max(uid_numbers, key=lambda u: u.uidNumber).uidNumber.value)
        uid_number = max_uid + 1
    except ValueError:
        uid_number = starting_uid_number

    # TODO make home directory
    # TODO chmod home directory
    # TODO copy in skel for home directory
    # TODO copy in SSH keys

    user_dict = {
        'objectClass': [
            'top',
            'person',
            'organizationalPerson',
            'inetOrgPerson',
            'posixAccount',
        ],
        'cn': uid,
        'givenName': given_name,
        'sn': sn,
        'uid': uid,
        'uidNumber': uid_number,
        'gidNUmber': gid_number,
        'homeDirectory': str(home_root / uid),
        'loginShell': '/bin/bash',
    }
    conn.strategy.add_entry(f'cn={uid},{BASE_DN}', user_dict)

    # TODO recursively chown home directory
