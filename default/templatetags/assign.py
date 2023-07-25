# Framework
from django.template import Library

register = Library()

@register.simple_tag
def define(value = None):
    return value
