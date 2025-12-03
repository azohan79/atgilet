from django.urls import path
from .views import under_construction

app_name = "maintenance"

urlpatterns = [
    path("", under_construction, name="maintenance"),
]
