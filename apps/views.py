import time
from pathlib import Path

import psutil
import yaml
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.models import App, Job


def get_apps():
    apps_root_dir = Path("/opt/apps")
    subdirs = (x for x in apps_root_dir.iterdir() if x.is_dir())
    apps_dirs = (s for s in subdirs if (s / "meta.yaml").exists())
    apps = {a.name: yaml.safe_load((a / "meta.yaml").read_text()) for a in apps_dirs}
    return apps


def get_app_state(apps):
    set_apps = {}

    for a, m in apps.items():
        try:
            state = App.objects.get(pk=a).get_state_display()
        except App.DoesNotExist:
            state = "Not installed"
        set_apps[a] = m.update({"state": state})
        pass
    return apps


def update_job_states():
    # TODO Check for failure
    for job in Job.objects.filter(state="R"):
        print("Checking job", job)
        try:
            p = psutil.Process(job.pid)
            if str(hash(p)) == job.hash:
                # We've got the correct process
                print("Process found:", p, p.status())
                if p.status() not in {psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING, psutil.STATUS_DISK_SLEEP, psutil.STATUS_WAKING, psutil.STATUS_IDLE}:
                    raise psutil.NoSuchProcess(job.pid)
            else:
                raise psutil.NoSuchProcess(job.pid)
        except psutil.NoSuchProcess:
            print("Job has finished")
            job.state = "C"
            job.save()
            job.app.state = "I"  # TODO check for deletion task
            job.app.save()


@login_required
def index(request):
    """
    List all the available apps and which ones are installed.
    """

    update_job_states()

    apps = get_apps()
    apps = get_app_state(apps)

    return render(request, "apps/index.html", {
        "apps": apps,
    })


@login_required
def app(request, name):
    update_job_states()

    # This might be nicer to be a PUT but we can't send a PUT via HTML
    if request.method == "POST":
        requested_state = request.POST["state"]
        try:
            app_object = App.objects.get(name=name)
        except App.DoesNotExist:
            # If the app is not in the database, maybe its name is wrong
            if name not in get_apps():
                response = {
                    "name": name,
                    "state": "Not found",
                }
                return JsonResponse(response, status=404)
            # If the name is correct but it is not in the database, it must not be installed
            app_object = App.objects.update_or_create(name=name, defaults={"state": "U"})[0]

        if requested_state == "installed":
            if app_object.state in {"U", "F"}:
                # Kick off the installation

                p = psutil.Popen(["/bin/sleep", "1"])  # TODO call correct installer
                j = Job(app=app_object, pid=p.pid, hash=str(hash(p)), state="R")
                j.save()

                app_object.state = "P"
                app_object.save()

                messages.info(request, f"{get_apps()[name]['name']} is being installed")
                return redirect('index')
        elif requested_state == "absent:":
            if app_object.state in {"I", "P"}:
                # Delete the app
                ...  # TODO delete the app
                app_object.state = "U"
                app_object.save()

                messages.info(request, f"{get_apps()[name]['name']} is being deleted")
                return redirect('index')
        else:
            pass  # TODO error, requested state not recognised

    if name in get_apps():
        try:
            state = App.objects.get(name=name).get_state_display()
        except App.DoesNotExist:
            state = "Not installed"
        response = {
            "name": name,
            "state": state,
        }
        return JsonResponse(response)
    else:
        response = {
            "name": name,
            "state": "App not found",
        }
        return JsonResponse(response, status=404)
