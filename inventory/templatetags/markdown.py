# Python
import markdown
# Django
from django import template

register = template.Library()

@register.filter(name = 'markdownify')
def markdownify(value):
    return markdown.markdown(value, safe_mode = 'escape')
