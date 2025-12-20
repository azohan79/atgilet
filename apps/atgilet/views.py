from siteconfig.models import SettingsConfig
from maintenance.views import under_construction
from web.views import home as web_home


def front_router(request):
    """
    Если сайт в режиме разработки:
    - для обычных показываем maintenance
    - для админов (is_staff=True) показываем основной сайт.
    Если режим разработчика выключен, всем показываем основной сайт.
    """

    settings = SettingsConfig.objects.first()
    # если настроек нет — считаем, что сайт в разработке (как у тебя было)
    maintenance = settings.maintenance_mode if settings else True

    user = request.user
    is_admin = user.is_authenticated and user.is_staff

    if maintenance and not is_admin:
        # режим "сайт в разработке" для всех, кроме админов
        return under_construction(request)

    # основной сайт
    return web_home(request)