from siteconfig.models import SiteSettings
from maintenance.views import under_construction
from web.views import home as web_home


def front_router(request):
    """
    Если сайт в режиме разработки:
      - для обычных пользователей показываем maintenance
      - для админов (is_staff=True) показываем основной сайт
    Если режим разработки выключен — всем показываем основной сайт.
    """
    settings = SiteSettings.objects.first()
    maintenance = settings.maintenance_mode if settings else True  # если настроек нет — считаем, что сайт в разработке

    user = request.user
    is_admin = user.is_authenticated and user.is_staff

    if maintenance and not is_admin:
        # режим "сайт в разработке" для всех, кроме админов
        return under_construction(request)

    # основной сайт
    return web_home(request)
