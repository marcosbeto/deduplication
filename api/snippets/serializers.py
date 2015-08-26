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
