from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from citc.forms import UserForm
from citc.users import get_all_users, create_user


@login_required
def index(request):
    return render(request, "index.html")


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
