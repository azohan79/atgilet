from django.urls import path
from .views import maintenance_page

app_name = "maintenance"

urlpatterns = [
    path("", maintenance_page, name="maintenance"),
]
