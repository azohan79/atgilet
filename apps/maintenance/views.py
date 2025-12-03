from django.shortcuts import render


def under_construction(request):
    """
    Страница «сайт в разработке»
    """
    return render(request, "maintenance/index.html")


# Чтобы можно было использовать и старое имя, если где-то появится
maintenance_page = under_construction