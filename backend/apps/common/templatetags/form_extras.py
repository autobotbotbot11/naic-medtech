from django import template


register = template.Library()


@register.filter
def bound_field(form, field_name):
    return form[field_name]
