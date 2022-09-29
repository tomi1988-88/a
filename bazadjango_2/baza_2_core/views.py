from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect

from .models import Tag
from .models import Entry
from .models import Industry
from .models import Court
from .models import Scope

from django.db.models import Q
import datetime as dt
from functools import reduce
from operator import and_, or_


# Create your views here.

def home(request):
    tags = Tag.objects.all()
    tag_category = Tag.objects.values_list("category", flat=True).distinct()

    industry = Industry.objects.all()
    court = Court.objects.all()
    scope = Scope.objects.all()
    context = {"tag_category": tag_category, "tags": tags, "industry": industry, "court": court, "scope": scope}

    return render(request, "home.html", context)


def results(request):
    data = request.POST

    full_base = data.get("full_base")
    act_signature = data.get("act_signature")
    dec_number = data.get("dec_number")
    description = data.get("description")
    company = [v for k, v in data.items() if ("company" in k) and v]

    all_courts = {x.abbreviation: x.court for x in Court.objects.all()}
    court = [k for k, v in data.items() if k in all_courts.keys()]

    all_scope = {"{}scope".format(x.scope): "{}scope".format(x.id) for x in Scope.objects.all()}
    scope = [k for k, v in data.items() if k in all_scope.keys()]

    all_industry = {"{}industry".format(x.industry): "{}industry".format(x.id)  for x in Industry.objects.all()}
    industry = [k for k, v in data.items() if k in all_industry.keys()]

    key_words = [key for key, val in data.items() if key not in ["narrow_search",
                                                                 "csrfmiddlewaretoken",
                                                                 "description",
                                                                 "company-1",
                                                                 "company-2",
                                                                 "company-3",
                                                                 "company-4",
                                                                 "company-5",
                                                                 "data-od",
                                                                 "data-do"]]
    key_words = [key for key in key_words if key not in court]
    key_words = [key for key in key_words if key not in scope]
    key_words = [key for key in key_words if key not in industry]

    key_words_positive = [k for k in key_words if not ("-" in k)]
    key_words_negative = [k[1:] for k in key_words if ("-" in k)]

    narrow_search = data.get("narrow_search")

    data_od = dt.datetime.strptime(data.get("data-od"), "%Y-%m-%d") if data.get("data-od") else None
    data_do = dt.datetime.strptime(data.get("data-do"), "%Y-%m-%d") if data.get("data-do") else None

    sort_date_descending = data.get("sort_date_descending")
    sort_date_ascending = data.get("sort_date_ascending")
    sort_company_descending = data.get("sort_company_descending")
    sort_company_ascending = data.get("sort_company_ascending")

    sort_court_descending = data.get("sort_court_descending")
    sort_court_ascending =data.get("sort_court_ascending")


    if not(act_signature) and "act_signature" in data.keys() and not(full_base): # if you send empty form
        query = Entry.objects.all().order_by("date_of_dec")
        context = {"query": query, "act_signature": "Nie podałeś/aś sygnatury przy wyszukiwaniu", "length": len(query)}
        return render(request, "results.html", context)

    if not(dec_number) and "dec_number" in data.keys() and not(full_base): # if you send empty form
        query = Entry.objects.all().order_by("date_of_dec")
        context = {"query": query, "act_signature": "Nie podałeś/aś numeru decyzji przy wyszukiwaniu", "length": len(query)}
        return render(request, "results.html", context)

    if full_base:
        query = Entry.objects.all().order_by("date_of_dec")

        context = {"query": query, "full_base": "Wyświetlam całą zawartość bazy", "length": len(query)}
        return render(request, "results.html", context)

    if not(any(val for val in list(data.values())[1:])):       # if you send empty form

        query = Entry.objects.all().order_by("date_of_dec")
        context = {"query": query, "full_base": "Nie podałeś/aś szczegółowych kryteriów wyszukiwania", "length": len(query)}
        return render(request, "results.html", context)

    if act_signature:
        query = Entry.objects.filter(act_signature__contains=act_signature)
        context = {"query": query, "act_signature": act_signature, "length": len(query)}
        return render(request, "results.html", context)

    if dec_number:
        query = Entry.objects.filter(source_dec__contains=dec_number)
        context = {"query": query, "dec_number": dec_number, "length": len(query)}
        return render(request, "results.html", context)

    if (data_od and not data_do) or (not data_od and data_do):
        context = {
            "data_od": data_od,
            "data_do": data_do,
            "wrong_date": "Nieścisłość w polach 'Wyszukaj wg dat': należy pozostawić oba pola puste albo wypełnić daty w obu. Kliknij 'Powrót do wyszukiwania' "
        }
        return render(request, "results.html", context)

    if data_od and data_do:
        if data_do < data_od:
            print("Nieścisłość w polach 'Wyszukaj wg dat': data 'od' późniejsza niż data 'do'")
            context = {
                "data_od": data_od,
                "data_do": data_do,
                "wrong_date": "Nieścisłość w polach 'Wyszukaj wg dat': data 'od' późniejsza niż data 'do'. Kliknij 'Powrót do wyszukiwania'"
            }
            return render(request, "results.html", context)

    if sort_date_ascending:

        sort_date_ascending = sort_date_ascending.split("\r\n")
        sort_date_ascending = {k: v for k, v in (x.split(":") for x in sort_date_ascending)}
        sort_date_ascending = {k: (None if v == "None" else v) for k, v in sort_date_ascending.items()}

        pk_lst = sort_date_ascending["id"].split(";")[:-1]


        query = Entry.objects.filter(pk__in=pk_lst).order_by("date_of_dec")

        context = {"query": query, "length": len(query), **sort_date_ascending}
        return render(request, "results.html", context)

    if sort_date_descending:

        sort_date_descending = sort_date_descending.split("\r\n")
        sort_date_descending = {k: v for k, v in (x.split(":") for x in sort_date_descending)}
        sort_date_descending = {k: (None if v == "None" else v) for k, v in sort_date_descending.items()}

        pk_lst = sort_date_descending["id"].split(";")[:-1]

        query = Entry.objects.filter(pk__in=pk_lst).order_by("-date_of_dec")

        context = {"query": query, "length": len(query), **sort_date_descending}
        return render(request, "results.html", context)

    if sort_company_ascending:

        sort_company_ascending = sort_company_ascending.split("\r\n")
        sort_company_ascending = {k: v for k, v in (x.split(":") for x in sort_company_ascending)}
        sort_company_ascending = {k: (None if v == "None" else v) for k, v in sort_company_ascending.items()}
        pk_lst = sort_company_ascending["id"].split(";")[:-1]

        query = Entry.objects.filter(pk__in=pk_lst).order_by("company")

        context = {"query": query, "length": len(query), **sort_company_ascending}
        return render(request, "results.html", context)

    if sort_company_descending:

        sort_company_descending = sort_company_descending.split("\r\n")
        sort_company_descending = {k: v for k, v in (x.split(":") for x in sort_company_descending)}
        sort_company_descending = {k: (None if v == "None" else v) for k, v in sort_company_descending.items()}
        pk_lst = sort_company_descending["id"].split(";")[:-1]

        query = Entry.objects.filter(pk__in=pk_lst).order_by("-company")

        context = {"query": query, "length": len(query), **sort_company_descending}
        return render(request, "results.html", context)

    if sort_court_ascending:
        sort_court_ascending = sort_court_ascending.split("\r\n")
        sort_court_ascending = {k: v for k, v in (x.split(":") for x in sort_court_ascending)}
        sort_court_ascending = {k: (None if v == "None" else v) for k, v in sort_court_ascending.items()}
        pk_lst = sort_court_ascending["id"].split(";")[:-1]

        query = Entry.objects.filter(pk__in=pk_lst).order_by("court")

        context = {"query": query, "length": len(query), **sort_court_ascending}
        return render(request, "results.html", context)

    if sort_court_descending:

        sort_court_descending = sort_court_descending.split("\r\n")
        sort_court_descending = {k: v for k, v in (x.split(":") for x in sort_court_descending)}
        sort_court_descending = {k: (None if v == "None" else v) for k, v in sort_court_descending.items()}
        pk_lst = sort_court_descending["id"].split(";")[:-1]

        query = Entry.objects.filter(pk__in=pk_lst).order_by("-court")

        context = {"query": query, "length": len(query), **sort_court_descending}
        return render(request, "results.html", context)

    if description or company or (data_od and data_do) or court or scope or industry or key_words:  # regular search
        print("jestem w regula search")
        query = Entry.objects.filter(
                    Q(subject_of_act__contains=description) |
                    Q(main_allegations__contains=description) |
                    Q(court_theses__contains=description) |
                    Q(quotes__contains=description)
                )

        if company:
            q_expressions = []

            for c in company:
                q_expressions.append(Q(company__contains=c))

            q_expressions = reduce(or_, q_expressions)
            query = query.filter(q_expressions)

        if court:
            q_expressions = []

            for c in court:
                q_expressions.append(Q(court__contains=c))

            q_expressions = reduce(or_, q_expressions)
            query = query.filter(q_expressions)

        if industry:
            q_expressions = []

            for c in [all_industry.get(x) for x in industry]:
                q_expressions.append(Q(industry__contains=c))

            q_expressions = reduce(or_, q_expressions)
            query = query.filter(q_expressions)

        if scope:
            q_expressions = []

            for c in [all_scope.get(x) for x in scope]:
                q_expressions.append(Q(scope__contains=c))

            q_expressions = reduce(or_, q_expressions)
            query = query.filter(q_expressions)

            for i in query:
                print(i.scope)

        if data_od and data_do:
            query = query.filter(
                        date_of_dec__gte=data_od
                    ).filter(
                        date_of_dec__lte=data_do
                    )

        if key_words_positive and narrow_search:

            q_expressions = []

            for k in key_words_positive:
                q_expressions.append(Q(key_words__contains=k))

            q_expressions = reduce(and_, q_expressions)
            query = query.filter(q_expressions)

        if key_words_positive and not(narrow_search):

            q_expressions = []

            for k in key_words_positive:
                q_expressions.append(Q(key_words__contains=k))

            q_expressions = reduce(or_, q_expressions)
            query = query.filter(q_expressions)

        if key_words_negative:

            q_expressions = []

            for k in key_words_negative:
                q_expressions.append(Q(key_words__contains=k))

            q_expressions = reduce(or_, q_expressions)
            query = query.exclude(q_expressions)

        context = {"query": query,
                   "length": len(query),
                   "description": description,
                   "company": company,
                   "data_od": data_od,
                   "data_do": data_do,
                   "court": court,
                   "industry": industry,
                   "scope": scope,
                   "key_words_positive": key_words_positive,
                   "narrow_search": narrow_search,
                   "key_words_negative": key_words_negative,
                   }
        return render(request, "results.html", context)


def act(request, pk):
    query = Entry.objects.get(pk=pk)
    context = {"query": query}
    return render(request, "act.html", context)

