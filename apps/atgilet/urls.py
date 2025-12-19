from django.contrib import admin
from django.urls import path, include
from .views import front_router

urlpatterns = [
    path("admin/", admin.site.urls),

    # корень сайта — динамический роутер
    path("", front_router, name="home"),

    # прямые адреса (если нужно заходить напрямую)
    path("web/", include("web.urls")),
    path("maintenance/", include("maintenance.urls")),
    path("news/", include("news.urls", namespace="news")),
]
