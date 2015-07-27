from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from djangotoolbox.fields import ListField, DictField
from django_mongodb_engine.contrib import MongoDBManager

class Snippet(models.Model):
    rea = ListField()

    objects = MongoDBManager()

    # class Meta:
    #     ordering = ('rea',)