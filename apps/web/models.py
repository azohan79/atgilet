from django.db import models

class HomePage(models.Model):
    """
    Singleton-настройки главной.
    Держим 1 запись (id=1), правим в админке.
    """
    title = models.CharField(max_length=200, default="Home", blank=True)
    
    # Блок 1 — Слайдер (общие тексты/кнопки по умолчанию)
    hero_title_part1 = models.CharField(max_length=120, blank=True)
    hero_title_part2 = models.CharField(max_length=120, blank=True)
    hero_subtitle = models.CharField(max_length=200, blank=True)

    hero_btn1_text = models.CharField(max_length=60, blank=True)
    hero_btn1_url = models.CharField(max_length=300, blank=True)
    hero_btn2_text = models.CharField(max_length=60, blank=True)
    hero_btn2_url = models.CharField(max_length=300, blank=True)

    # Блок 2 (о клубе)
    about_vertical_title = models.CharField(max_length=120, blank=True)
    about_title = models.CharField(max_length=200, blank=True)
    about_text = models.TextField(blank=True)
    about_btn_text = models.CharField(max_length=60, blank=True)
    about_btn_url = models.CharField(max_length=300, blank=True)

    # Блок 3 (анонс игры)
    match_title = models.CharField(max_length=200, blank=True)
    match_text = models.TextField(blank=True)
    match_btn1_text = models.CharField(max_length=60, blank=True)
    match_btn1_url = models.CharField(max_length=300, blank=True)
    match_btn2_text = models.CharField(max_length=60, blank=True)
    match_btn2_url = models.CharField(max_length=300, blank=True)

    # Блок 4 (последние результаты — пока статично)
    results_vertical_title = models.CharField(max_length=120, blank=True)
    results_btn_text = models.CharField(max_length=60, blank=True)
    results_btn_url = models.CharField(max_length=300, blank=True)

    # Блок 5 (цифры) — элементы отдельной моделью (см. ниже)

    # Блок 7 (видео)
    video_title = models.CharField(max_length=200, blank=True)
    video_iframe_url = models.CharField(max_length=500, blank=True)  # ссылка на embed
    video_poster = models.ImageField(upload_to="home/video/", blank=True, null=True)

    # Блок 8 (топ/категории — пока статично)
    top_vertical_title = models.CharField(max_length=120, blank=True)
    top_title = models.CharField(max_length=200, blank=True)
    top_text = models.TextField(blank=True)
    top_btn_text = models.CharField(max_length=60, blank=True)
    top_btn_url = models.CharField(max_length=300, blank=True)

    # Блок 9 (турнирная таблица — динамический, но заголовок/кнопка статично)
    table_title = models.CharField(max_length=200, blank=True)
    table_btn_text = models.CharField(max_length=60, blank=True)
    table_btn_url = models.CharField(max_length=300, blank=True)

    # Блок 10 (новости — динамика, но кнопка статично)
    news_btn_text = models.CharField(max_length=60, blank=True)
    news_btn_url = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return "HomePage settings"

class HomeSliderSlide(models.Model):
    home = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="slides")
    order = models.PositiveIntegerField(default=1)

    # что менять на слайде
    hero_image = models.ImageField(upload_to="home/slider/", blank=True, null=True)

    # (опционально) индивидуальные тексты/кнопки; если пусто — брать из HomePage
    title_part1 = models.CharField(max_length=120, blank=True)
    title_part2 = models.CharField(max_length=120, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)

    btn1_text = models.CharField(max_length=60, blank=True)
    btn1_url = models.CharField(max_length=300, blank=True)
    btn2_text = models.CharField(max_length=60, blank=True)
    btn2_url = models.CharField(max_length=300, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Slide #{self.order}"

class HomeStatItem(models.Model):
    home = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="stats")
    order = models.PositiveIntegerField(default=1)

    value = models.CharField(max_length=20, blank=True)   # "2700"
    label = models.CharField(max_length=80, blank=True)   # "Goals"

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.value} {self.label}"