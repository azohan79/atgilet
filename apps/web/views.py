from django.shortcuts import render


def home(request):
    """
    Главная страница основного сайта ATGilet.
    Пока простая заглушка, позже сюда прикрутим нормальный layout.
    """
    return render(request, "web/index.html")