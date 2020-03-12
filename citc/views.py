import subprocess

from ansi2html import Ansi2HTMLConverter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from citc.forms import UserForm
from citc.users import get_all_users, create_user


@login_required
def index(request):
    slurmctld_status = subprocess.run(["systemctl", "is-active", "slurmctld"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    slurmctld_status = slurmctld_status.stdout.decode().strip()

    slurmctld_log = subprocess.run(["journalctl", "--unit", "slurmctld"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    slurmctld_log = slurmctld_log.stdout.decode()
    conv = Ansi2HTMLConverter(inline=True)
    slurmctld_log = conv.convert(slurmctld_log, full=False)
    slurmctld_log = "<br>\n".join(slurmctld_log.split("\n"))

    return render(request, "index.html", {
        "slurmctld_status": slurmctld_status,
        "slurmctld_log": slurmctld_log,
    })


@login_required
def users(request):
    from citc.users import connection
    conn = connection()
    users = get_all_users(conn)

    context = {"users": users}

    return render(request, "users.html", context)


@login_required
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            uid = form.cleaned_data['uid']
            given_name = form.cleaned_data['given_name']
            sn = form.cleaned_data['sn']
            keys = form.cleaned_data['keys']

            from citc.users import connection
            conn = connection()
            create_user(conn, uid, given_name, sn, keys)

            return HttpResponseRedirect(reverse('users'))
    else:
        form = UserForm()

    return render(request, 'add_user.html', {'form': form})
