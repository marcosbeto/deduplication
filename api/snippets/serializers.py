from django.forms import widgets
from rest_framework import serializers
from snippets.models import Snippet
from snippets.models import Grouped_number_of_ads_equals
from djangotoolbox.fields import ListField, DictField


class SnippetSerializer(serializers.Serializer):
    rea = serializers.ListField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.rea = validated_data.get('rea', instance.rea)
        instance.save()
        return instance

class SnippetSerializer_Numbers(serializers.Serializer):
    reas = serializers.ListField()
    noe = serializers.models.IntegerField()
    nog = serializers.models.IntegerField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Grouped_number_of_ads_equals.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.reas = validated_data.get('reas', instance.reas)
        instance.noe = validated_data.get('noe', instance.noe)
        instance.nog = validated_data.get('nog', instance.nog)
        instance.save()
        return instance

class SnippetSerializer_Grouped_Filtered(serializers.Serializer):
    reas = serializers.ListField()
    equal_filters = serializers.IntegerField()
    precio = serializers.ListField()
    idtipodeoperacion = serializers.ListField()
    idzona = serializers.ListField()
    idtipodepropiedad = serializers.ListField()
    titulo = serializers.ListField()
    direccion = serializers.ListField()
    idavisopadre = serializers.ListField()
    idempresa = serializers.ListField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Ads_equals_filtered_grouped.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """

        instance.reas = validated_data.get('reas', instance.reas) 
        instance.equal_filters = validated_data.get('equal_filters', instance.equal_filters) 
        instance.precio = validated_data.get('precio', instance.precio) 
        instance.idtipodeoperacion = validated_data.get('idtipodeoperacion', instance.idtipodeoperacion) 
        instance.idzona = validated_data.get('idzona', instance.idzona) 
        instance.idtipodepropiedad = validated_data.get('idtipodepropiedad', instance.idtipodepropiedad) 
        instance.titulo = validated_data.get('titulo', instance.titulo) 
        instance.direccion = validated_data.get('direccion', instance.direccion) 
        instance.idavisopadre = validated_data.get('idavisopadre', instance.idavisopadre) 
        instance.idempresa = validated_data.get('idempresa', instance.idempresa) 
    
        instance.save()
        return instance