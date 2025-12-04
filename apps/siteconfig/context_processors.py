from .models import Menu


def header_footer_menus(request):
    locations = [
        Menu.HEADER_MAIN_LEFT,
        Menu.HEADER_MAIN_RIGHT,
        Menu.HEADER_TOP_AUTH,
        Menu.HEADER_TOP_SOCIAL,
        Menu.MOBILE_MAIN_LEFT,
        Menu.MOBILE_MAIN_RIGHT,
        Menu.FOOTER_TAGS,
        Menu.FOOTER_BOTTOM,
    ]
    menus = (
        Menu.objects.filter(location__in=locations, is_active=True)
        .prefetch_related("items__children")
    )

    ctx = {}
    for m in menus:
        ctx[f"menu_{m.location}"] = m
    return ctx
