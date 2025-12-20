from django.contrib import admin
from django.urls import path, include
from .views import front_router


urlpatterns = [
    path("admin/", admin.site.urls),

    # прямые адреса (если нужно заходить напрямую)
    path("", include("web.urls")),
    path("maintenance/", include("maintenance.urls")),
    path("news/", include("news.urls", namespace="news")),
    path("gallery/", include("apps.photo_gallery.urls")),
    
    # корень сайта — динамический роутер
    path("", front_router, name="home"),
]

handler404 = "web.views.page_not_found"
