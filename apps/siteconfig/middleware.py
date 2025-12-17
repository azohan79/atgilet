from django.conf import settings
from django.utils import translation

SUPPORTED = {code for code, _ in settings.LANGUAGES}
DEFAULT = settings.LANGUAGE_CODE

class ForceDefaultLanguageMiddleware:
    """
    Если язык не выбран пользователем (нет cookie django_language),
    то принудительно используем LANGUAGE_CODE (у вас 'es').
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        if not cookie_lang or cookie_lang not in SUPPORTED:
            translation.activate(DEFAULT)
            request.LANGUAGE_CODE = DEFAULT

        response = self.get_response(request)
        translation.deactivate()
        return response
