from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def transform_query(context, **parameters):
    """
    **parametersの値に基づいてrequest.GETのパラメータを変更し、
    文字列形式（urlencode）で変更後のパラメータを返す。
    """
    query = context["request"].GET.copy()
    for key in parameters:
        query[key] = parameters[key]

    return query.urlencode()
