from copy import copy

import yaml
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ldap3 import Server, Connection, MOCK_SYNC, ALL_ATTRIBUTES


@login_required
def index(request):
    return render(request, "index.html")


@login_required
def users(request):
    base_dn = "ou=People,dc=citc,dc=acrc,dc=bristol,dc=ac,dc=uk"
    if settings.IN_PRODUCTION:
        with open("/etc/citc/webui.yaml", "r") as f:
            config = yaml.safe_load(f)
        connection = Connection('ldap://localhost', user='cn=Directory Manager', password=config["ldap_password"], auto_bind=True)
    else:
        server = Server('my_fake_server')
        connection = Connection(server, user='cn=Directory Manager', password='my_password', client_strategy=MOCK_SYNC)
        connection.strategy.add_entry(f'cn=matt,{base_dn}',
                                      {
                                          'objectClass': [
                                              'top',
                                              'person',
                                              'organizationalPerson',
                                              'inetOrgPerson',
                                              'posixAccount',
                                          ],
                                          'cn': 'matt',
                                          'givenName': 'Matt',
                                          'sn': 'Williams',
                                          'uid': 'matt',
                                          'uidNumber': 10001,
                                          'gidNUmber': 100,
                                          'homeDirectory': '/mnt/shared/home/matt',
                                          'loginShell': '/bin/bash',
                                      })
        connection.bind()
    connection.search('ou=People,dc=citc,dc=acrc,dc=bristol,dc=ac,dc=uk', '(objectclass=posixAccount)', attributes=ALL_ATTRIBUTES)
    users = copy(connection.entries)

    context = {"users": users}

    return render(request, "users.html", context)
