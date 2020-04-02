from pathlib import Path

import yaml
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.models import Apps


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
            state = Apps.objects.get(pk=a).get_state_display()
        except Apps.DoesNotExist:
            state = "Not installed"
        set_apps[a] = m.update({"state": state})
        pass
    return apps


@login_required
def index(request):
    """
    List all the available apps and which ones are installed.
    """

    apps = get_apps()
    apps = get_app_state(apps)

    return render(request, "apps/index.html", {
        "apps": apps,
    })
