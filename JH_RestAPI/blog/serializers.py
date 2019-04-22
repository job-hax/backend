from rest_framework import serializers
from . import models


class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'title', 'content', 'image', 'is_html', 'created_at',)
        model = models.Blog

class BlogSnippetSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'title', 'snippet', 'image', 'created_at',)
        model = models.Blog        