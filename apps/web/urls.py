from django.urls import path
from .views import home

app_name = "web"

urlpatterns = [
    path("", home, name="home"),
    path("history/", views.history, name="history"),
    path("school/valencia-cf/", views.school_valencia_cf, name="school_valencia_cf"),
    path("school/academy/", views.school_academy, name="school_academy"),
    path("sponsors/", views.sponsors, name="sponsors"),
    path("contacts/", views.contacts, name="contacts"),
]
