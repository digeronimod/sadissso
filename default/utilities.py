# Python
import django, re
from urllib import parse
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
# Plugins
from mailqueue.models import MailerMessage
# Django
from django.db.models import Q
from django.template.loader import render_to_string

## -- EMAIL
def queue_html_email(recipient, subject, template, context, cc_recipients = None):
    content = render_to_string(template, context)

    message = MailerMessage()
    message.to_address = recipient

    if cc_recipients != None:
        message.cc_address = cc_recipients

    message.subject = subject
    message.html_content = content

    message.save()

## -- NUMBERS
def make_ordinal(n):
    try:
        n = int(n)
    except:
        return n

    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]

    if 11 <= (n % 100) <= 13:
        suffix = 'th'

    return str(n) + suffix

## -- QUERIES
def normalize_query(qstring, terms = re.compile(r'"([^"]+)"|(\S+)').findall, normalize = re.compile(r'\s{2,}').sub):
    return [normalize(' ', (term[0] or term[1]).strip()) for term in terms(qstring)]

def get_query(qstring, search_fields):
    query = None
    terms = normalize_query(qstring)

    for term in terms:
        or_query = None

        for field_name in search_fields:
            q = Q(**{'%s__icontains' % field_name: term})

            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q

        if query is None:
            query = or_query
        else:
            query = query & or_query

    return query

def get_filters(url, allowed):
    query = parse.urlsplit(url).query
    pack = dict(parse.parse_qsl(query))
    translated = {}

    for pk, pv in pack.items():
        if pk in allowed:
            translated[allowed[pk]] = pv

    return translated

## -- STRINGS
def is_blank(string):
    return not (string and string.strip())

def is_not_blank(string):
    return bool(string and string.strip())

## -- URLS
class Qurl(object):
    def __init__(self, url):
        self.url = url
        self._qsl = parse_qsl(urlparse(url).query)

    def set(self, name, value):
        clone = self._clone()

        if django.VERSION[0] <= 1 and django.VERSION[1] <= 4:
            value = value or None

        clone._qsl = [(q, v) for (q, v) in self._qsl if q != name]

        if value is not None:
            clone._qsl.append((name, value))

        return clone

    def add(self, name, value):
        clone = self._clone()
        clone._qsl = [p for p in self._qsl if not(p[0] == name and p[1] == value)]

        clone._qsl.append((name, value,))

        return clone

    def remove(self, name, value):
        clone = self._clone()
        clone._qsl = [qb for qb in self._qsl if qb != (name, str(value))]

        return clone

    def inc(self, name, value=1):
        clone = self._clone()
        clone._qsl = [(q, v) if q != name else (q, int(v) + value) for (q, v) in self._qsl]

        if name not in dict(clone._qsl).keys():
            clone._qsl.append((name, value))

        return clone

    def dec(self, name, value=1):
        return self._clone().inc(name, -value)

    def _clone(self):
        return Qurl(self.get())

    def get(self):
        parsed = list(urlparse(self.url))
        parsed[4] = urlencode(self._qsl)

        return urlunparse(parsed)
