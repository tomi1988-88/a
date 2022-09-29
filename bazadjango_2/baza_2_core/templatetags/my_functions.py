import ast
import datetime as dt

from django import template
from ..models import Scope
from ..models import Entry


register = template.Library()


@register.filter
def key_words_trimmer(value):

    dictionary = value.__dict__.get("choices")

    list_of_val = [int(x) for x in list(value) if int(x) in dictionary.keys()]

    list_of_val = list(map(dictionary.get, list_of_val))

    val = ", ".join([x.split(" / ")[1] for x in list_of_val])

    return val


@register.filter
def key_words_translate(value):
    if type(value) == str:
        value = ast.literal_eval(value)

    if value:
        dictionary = Entry.objects.last().__dict__.get("key_words").__dict__.get("choices")

        list_of_val = [int(x) for x in value if int(x) in dictionary.keys()]
        list_of_val = list(map(dictionary.get, list_of_val))

        val = ", ".join([x.split(" / ")[1] for x in list_of_val])

        return val
    else:
        return ""

@register.filter
def date_to_empty_str(value):
    if value is None:
        return ""
    elif type(value) == str:
        return value
    else:
        return dt.datetime.strftime(value, "%d-%m-%Y")


@register.filter
def court_results_translate(value):
    if type(value) == str:
        value = ast.literal_eval(value)
    return ", ".join(value)


@register.filter
def industry_results_translate(value):
    if type(value) == str:
        value = ast.literal_eval(value)
    value = [v[:-8] for v in value]
    return ", ".join(value)

@register.filter
def scope_results_translate(value):
    if type(value) == str:
        value = ast.literal_eval(value)
    value = [v[:-5] for v in value]
    return ", ".join(value)

@register.filter
def scope_translate(value):

    dictionary = {"{}scope".format(x.id): x.scope for x in Scope.objects.all()}

    return dictionary.get(value)


