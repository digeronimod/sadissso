from django import template

register = template.Library()

@register.filter(name = 'phone')
def phone(value):
    formatted = f'({value[0:3]}) {value[3:6]}-{value[6:10]}'

    return formatted
