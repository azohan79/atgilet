from django.views.generic import ListView, DetailView
from .models import Album


class AlbumListView(ListView):
    model = Album
    template_name = "photo_gallery/album_list.html"
    context_object_name = "albums"
    paginate_by = 8

    def get_queryset(self):
        return Album.objects.filter(is_published=True)


class AlbumDetailView(DetailView):
    model = Album
    template_name = "photo_gallery/album_detail.html"
    context_object_name = "album"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Album.objects.filter(is_published=True).prefetch_related("photos")
