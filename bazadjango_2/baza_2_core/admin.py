from django.contrib import admin
from .models import Tag
from .models import Industry
from .models import Scope
from .models import Court
from .models import Entry


# Register your models here.
from django import forms

class EntryModelForm(forms.ModelForm):
    subject_of_act = forms.CharField(widget=forms.Textarea)
    main_allegations = forms.CharField(widget=forms.Textarea)
    court_theses = forms.CharField(widget=forms.Textarea)
    quotes = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Entry
        fields = [
            "date_of_dec",
            "act_signature",
            "court",
            "type_of_dec",
            "company",
            "scope",
            "industry",
            "key_words",
            "previous_dec",
            "source_dec",
            "date_of_source_dec",
            "act_doc",
            "act_pdf",
            "subject_of_act",
            "main_allegations",
            "court_theses",
            "quotes",
            "related_acts"
                  ]

class EntryAdmin(admin.ModelAdmin):
    form = EntryModelForm

admin.site.register(Tag)
admin.site.register(Industry)
admin.site.register(Scope)
admin.site.register(Court)
admin.site.register(Entry, EntryAdmin)
