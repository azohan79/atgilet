from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # На корне сейчас будет maintenance
    path("", include("maintenance.urls")),

    # Основной сайт позже станет на корне
    path("web/", include("web.urls")),
]