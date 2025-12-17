from django.conf import settings
from django.utils import translation

SUPPORTED = {code for code, _ in settings.LANGUAGES}
DEFAULT = settings.LANGUAGE_CODE

class ForceDefaultLanguageMiddleware:
    """
    Если пользователь явно не выбирал язык (нет cookie django_language),
    то принудительно используем DEFAULT (у вас 'es'),
    даже если LocaleMiddleware выбрал другой по Accept-Language.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        if not cookie_lang or cookie_lang not in SUPPORTED:
            translation.activate(DEFAULT)
            request.LANGUAGE_CODE = DEFAULT

        return self.get_response(request)
