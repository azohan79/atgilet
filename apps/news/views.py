from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView, DetailView
from .models import NewsPost


class NewsListView(ListView):
    model = NewsPost
    template_name = "news/news_list.html"
    context_object_name = "posts"
    paginate_by = 6  # по вашей сетке 2 в ряд, 6 удобно

    def get_queryset(self):
        qs = NewsPost.objects.filter(is_published=True).select_related("category")

        # если published_at не заполнено — показываем по created_at через ordering модели
        # но для "не в будущем" можно ограничить:
        now = timezone.now()
        qs = qs.filter(Q(published_at__lte=now) | Q(published_at__isnull=True))

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))

        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        tag = self.request.GET.get("tag")
        if tag:
            # простая реализация для comma-separated tags
            qs = qs.filter(tags__icontains=tag)

        return qs


class NewsDetailView(DetailView):
    model = NewsPost
    template_name = "news/news_detail.html"
    context_object_name = "post"

