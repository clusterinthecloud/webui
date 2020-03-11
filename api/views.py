import yaml
from django.http import JsonResponse


def index(request):
    with open("/etc/citc/startnode.yaml", "r") as f:
        data = yaml.safe_load(f)

    safe_keys = {"cluster_id"}
    data = {k: v for k, v in data.items() if k in safe_keys}

    return JsonResponse(data)
