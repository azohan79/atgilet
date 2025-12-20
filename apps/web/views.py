from django.shortcuts import render
from .models import HomePage


def home(request):
    home_cfg = (
        HomePage.objects
        .prefetch_related("slides", "stats")
        .first()
    )

    slides = []
    stats = []
    if home_cfg:
        slides = [s for s in home_cfg.slides.all() if s.is_active]
        stats = list(home_cfg.stats.all())

    return render(request, "web/index.html", {
        "home_cfg": home_cfg,
        "slides": slides,
        "stats": stats,
    })
    
def history(request):
    return render(request, "web/history.html")

def school_valencia_cf(request):
    return render(request, "web/school_valencia_cf.html")

def school_academy(request):
    return render(request, "web/school_academy.html")

def sponsors(request):
    return render(request, "web/sponsors.html")

def contacts(request):
    return render(request, "web/contacts.html")

def page_not_found(request, exception):
    return render(request, "web/404.html", status=404)