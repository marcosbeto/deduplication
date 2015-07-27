from django.forms import widgets
from rest_framework import serializers
from snippets.models import Snippet
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
