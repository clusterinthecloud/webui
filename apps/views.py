from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """
    List all the available apps and which ones are installed.
    """
    return render(request, "index.html")
