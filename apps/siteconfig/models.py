from django.db import models


class SiteSettings(models.Model):
    maintenance_mode = models.BooleanField(
        "Сайт в разработке",
        default=True,
        help_text="Если включено, всем пользователям показывается страница 'сайт в разработке', кроме администраторов."
    )

    def __str__(self):
        return "Настройки сайта"

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"
