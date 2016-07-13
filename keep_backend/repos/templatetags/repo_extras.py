from django import template

register = template.Library()

@register.filter
def parse_label(value):
    if isinstance( value, basestring):
        return value
    else:
        return value[value.keys()[0]]
