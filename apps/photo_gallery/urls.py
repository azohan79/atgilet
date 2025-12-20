from django.urls import path
from .views import AlbumListView, AlbumDetailView

app_name = "photo_gallery"

urlpatterns = [
    path("", AlbumListView.as_view(), name="album_list"),
    path("<slug:slug>/", AlbumDetailView.as_view(), name="album_detail"),
]