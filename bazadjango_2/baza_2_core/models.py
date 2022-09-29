from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.


class Tag(models.Model):

    category = models.CharField(max_length=100, null=True)
    tag = models.CharField(max_length=200)

    class Meta:
        ordering = ["category"]

    def __str__(self):
        return "{} / {}".format(self.category, self.tag)


class Industry(models.Model):

    industry = models.CharField(max_length=200)

    class Meta:
        ordering = ["industry"]

    def __str__(self):
        return "{}".format(self.industry)

class Court(models.Model):

    court = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return "{} - {}".format(self.abbreviation, self.court)

class Scope(models.Model):

    scope = models.CharField(max_length=50)

    class Meta:
        ordering = ["-scope"]

    def __str__(self):
        return "{}".format(self.scope)

class Entry(models.Model):

    date_of_dec = models.DateField(default=None)
    act_signature = models.CharField(max_length=30, default=None)
    court = models.CharField(max_length=30, choices=[(x.abbreviation, x.court) for x in Court.objects.all()], null=True)
    type_of_dec = models.CharField(max_length=30)
    company = models.CharField(max_length=300)
    scope = models.CharField(max_length=30, choices=[("{}scope".format(x.id), "{}".format(x)) for x in Scope.objects.all()], null=True)
    industry = MultiSelectField(choices=[("{}industry".format(x.id,), "{}".format(x))for x in Industry.objects.all()], null=True)
    key_words = MultiSelectField(choices=[(x.id, "{} / {}".format(x.category, x.tag)) for x in Tag.objects.all()], null=True)
    previous_dec = models.CharField(max_length=400, blank=True)
    source_dec = models.CharField(max_length=30, blank=True)
    date_of_source_dec = models.DateField(null=True, blank=True)


    act_doc = models.FileField(upload_to="uploads/", null=True, blank=True)
    act_pdf = models.FileField(upload_to="uploads/", null=True, blank=True)

    subject_of_act = models.CharField(max_length=5000)
    main_allegations = models.CharField(max_length=8000)
    court_theses = models.CharField(max_length=10000)
    quotes = models.CharField(max_length=10000)

    related_acts = models.ManyToManyField('self', blank=True)
    def __str__(self):
        return "{} {} {} {}".format(self.date_of_dec, self.court, self.act_signature, self.company)


