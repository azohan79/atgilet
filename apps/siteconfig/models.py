from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language


class SettingsConfig(models.Model):
    maintenance_mode = models.BooleanField(
        "Сайт в разработке",
        default=True,
        help_text=(
            "Если включено, всем пользователям показывается страница "
            "'сайт в разработке', кроме администраторов."
        ),
    )

    def __str__(self):
        return "Настройки сайта"

    class Meta:
        verbose_name = "настройки сайта"
        verbose_name_plural = "настройки сайта"


class Menu(models.Model):
    """Набор пунктов меню для определённой зоны (хедер, футер и т.п.)."""

    HEADER_MAIN_LEFT = "header_main_left"
    HEADER_MAIN_RIGHT = "header_main_right"
    HEADER_TOP_AUTH = "header_top_auth"
    HEADER_TOP_SOCIAL = "header_top_social"
    MOBILE_MAIN_LEFT = "mobile_main_left"
    MOBILE_MAIN_RIGHT = "mobile_main_right"
    FOOTER_TAGS = "footer_tags"
    FOOTER_BOTTOM = "footer_bottom"

    LOCATION_CHOICES = [
        (HEADER_MAIN_LEFT, _("Хедер: главное меню слева")),
        (HEADER_MAIN_RIGHT, _("Хедер: главное меню справа")),
        (HEADER_TOP_AUTH, _("Хедер: авторизация / корзина / поиск")),
        (HEADER_TOP_SOCIAL, _("Хедер: соцсети")),
        (MOBILE_MAIN_LEFT, _("Моб. меню: левая колонка")),
        (MOBILE_MAIN_RIGHT, _("Моб. меню: правая колонка")),
        (FOOTER_TAGS, _("Футер: популярные теги")),
        (FOOTER_BOTTOM, _("Футер: нижнее меню")),
    ]

    name = models.CharField("Название", max_length=100)
    location = models.CharField(
        "Зона вывода",
        max_length=50,
        choices=LOCATION_CHOICES,
        unique=True,
    )
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "меню"
        verbose_name_plural = "меню"

    def __str__(self):
        return self.name

    @property
    def root_items(self):
        """Корневые пункты (без родителя)."""
        return self.items.filter(parent__isnull=True, is_active=True).order_by("order")


class MenuItem(models.Model):
    """Конкретный пункт меню (может иметь дочерние)."""

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Меню",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
        verbose_name="Родительский пункт",
    )

    # Мультиязычные заголовки (ES основной)
    title_es = models.CharField("Заголовок (ES)", max_length=200)
    title_val = models.CharField("Заголовок (VAL)", max_length=200, blank=True, default="")
    title_en = models.CharField("Заголовок (EN)", max_length=200, blank=True, default="")

    # URL: либо имя роута, либо явный путь
    named_url = models.CharField(
        "Имя URL (reverse)",
        max_length=100,
        blank=True,
        help_text="Имя url из urls.py (reverse). Имеет приоритет над полем 'URL'.",
    )
    url = models.CharField(
        "URL",
        max_length=255,
        blank=True,
        help_text="Абсолютный или относительный URL, если не используется имя роута.",
    )

    icon_class = models.CharField(
        "CSS-класс иконки",
        max_length=100,
        blank=True,
        help_text="Например: 'fa fa-shopping-cart', 'fa fa-facebook'.",
    )
    css_class = models.CharField(
        "Доп. CSS-класс",
        max_length=100,
        blank=True,
        help_text="Например: 'menu-item-has-children'.",
    )
    html_attributes = models.TextField(
        "Доп. HTML-атрибуты",
        blank=True,
        help_text=(
            'Например: data-toggle="modal" data-target="#tg-login". '
            "Выводится как есть в теге <a>."
        ),
    )

    open_in_new_tab = models.BooleanField("Открывать в новой вкладке", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ("order",)
        verbose_name = "пункт меню"
        verbose_name_plural = "пункты меню"

    def __str__(self):
        # чтобы в админке/логах было понятно даже при пустых VAL/EN
        return self.title_es

    def get_title(self, lang_code: str | None = None) -> str:
        """
        Возвращает заголовок по текущему языку сайта.
        Поддержка: es (base), val, en.
        Fallback: всегда на ES, если перевод пустой.
        """
        lang = (lang_code or get_language() or "es").lower()

        if lang.startswith("val"):
            return self.title_val or self.title_es
        if lang.startswith("en"):
            return self.title_en or self.title_es
        return self.title_es

    @property
    def title(self) -> str:
        """Удобно для шаблонов: {{ item.title }}"""
        return self.get_title()

    def get_url(self) -> str:
        from django.urls import reverse, NoReverseMatch

        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                # оставляем fallback, чтобы не падало в шаблонах
                pass
        return self.url or "#"

    @property
    def has_children(self) -> bool:
        return self.children.filter(is_active=True).exists()
