from django.db import models
from django.urls import reverse


class Album(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="gallery/covers/", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("photo_gallery:album_detail", kwargs={"slug": self.slug})


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="gallery/photos/")
    alt = models.CharField(max_length=255, blank=True)  # оставляем место для alt
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.album.title} — {self.id}"
