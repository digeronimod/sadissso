import re
from django import template

register = template.Library()

@register.filter(name = 'remove_parentheses')
def remove_parentheses(value):
    new_value = re.sub(r'\([^)]*\)', '', value)

    return new_value

@register.filter(name = 'only_parentheses')
def only_parentheses(value):
    try:
        new_value = re.findall('\((.*?)\)', value)[0]
    except:
        new_value = value

    return new_value
