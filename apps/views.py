from pathlib import Path

import yaml
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def get_apps():
    apps_root_dir = Path("/opt/apps")
    subdirs = (x for x in apps_root_dir.iterdir() if x.is_dir())
    apps_dirs = (s for s in subdirs if (s / "meta.yaml").exists())
    apps = {a.name: yaml.safe_load((a / "meta.yaml").read_text()) for a in apps_dirs}
    return apps


@login_required
def index(request):
    """
    List all the available apps and which ones are installed.
    """

    apps = get_apps()

    return render(request, "apps/index.html", {
        "apps": apps,
    })
