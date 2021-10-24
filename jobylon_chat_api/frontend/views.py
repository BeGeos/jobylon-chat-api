from django.shortcuts import render


def homepage(request):
    """
    Landing page for the website
    """
    return render(request, "index.html")
