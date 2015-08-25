from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from djangotoolbox.fields import ListField, DictField
from django_mongodb_engine.contrib import MongoDBManager

class Snippet(models.Model):
    rea = ListField()

    objects = MongoDBManager()

class Ads_equals_with_filters(models.Model):
    rea = ListField()
    id_aviso = models.IntegerField(null=True)

    objects = MongoDBManager()

class Ads_equals_filtered_grouped(models.Model):
    reas = ListField()
    equal_filters = models.IntegerField(null=True)
    precio = ListField()
    idtipodeoperacion = ListField()
    idzona = ListField()
    idtipodepropiedad = ListField()
    titulo = ListField()
    direccion = ListField()
    idavisopadre = ListField()
    idempresa = ListField()

    objects = MongoDBManager()
