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