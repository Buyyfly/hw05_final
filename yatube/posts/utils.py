from django.core.paginator import Paginator


def paginator_func(obj, settings, page):
    paginator = Paginator(obj, settings)
    page_obj = paginator.get_page(page)
    return page_obj
