from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class NewsCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class NewsPost(models.Model):
    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True, blank=True)

    # для списка (короткий текст)
    excerpt = models.TextField(blank=True)

    # основной контент (HTML допускается через админку)
    content = models.TextField()

    image = models.ImageField(upload_to="news/", blank=True, null=True)

    author_name = models.CharField(max_length=120, default="admin")
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
    )

    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags, e.g. sports, academy, camp",
    )

    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News post"
        verbose_name_plural = "News posts"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published", "published_at"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:240] or "post"
            slug = base
            i = 2
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tag_list(self):
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]