from django import template
register=template.Library()

@register.filter
def total(value, arg):
    return value*arg