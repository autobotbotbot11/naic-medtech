from django import template


register = template.Library()


@register.filter
def bound_field(form, field_name):
    return form[field_name]


@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name)
