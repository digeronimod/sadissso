# Python
import re
# Django
from django.utils.encoding import smart_str
from django.template import Library, Node, TemplateSyntaxError
# SADIS
from inventory.utilities import Qurl

register = Library()

@register.tag
def qurl(parser, token):
    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError(
            '"{0}" takes at least one argument (url)'.format(bits[0]))

    url = parser.compile_filter(bits[1])
    asvar = None
    bits = bits[2:]

    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    qs = []

    if len(bits):
        kwarg_re = re.compile(r'(\w+)(\-=|\+=|=|\+\+|\-\-)(.*)')

        for bit in bits:
            match = kwarg_re.match(bit)

            if not match:
                raise TemplateSyntaxError('Malformed arguments to url tag')

            name, op, value = match.groups()

            qs.append((name, op, parser.compile_filter(value),))

    return QURLNode(url, qs, asvar)

@register.tag
def rqurl(parser, token):
    return qurl(parser, token, True)

class QURLNode(Node):
    def __init__(self, url, qs, asvar):
        self.url = url
        self.qs = qs
        self.asvar = asvar

    def render(self, context):
        render_qurl = Qurl(self.url.resolve(context))

        for name, op, value in self.qs:
            name = smart_str(name)
            value = value.resolve(context)
            value = smart_str(value) if value is not None else None

            if op == '+=':
                render_qurl = render_qurl.add(name, value)
            elif op == '-=':
                render_qurl = render_qurl.remove(name, value)
            elif op == '=':
                render_qurl = render_qurl.set(name, value)
            elif op == '++':
                render_qurl = render_qurl.inc(name)
            elif op == '--':
                render_qurl = render_qurl.dec(name)

        url = render_qurl.get()

        if self.asvar:
            context[self.asvar] = url

            return ''
        else:
            return url
