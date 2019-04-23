from rest_framework import serializers
from . import models
import pytz


class BlogSerializer(serializers.ModelSerializer):

    def get_created_at(self, obj):
        if obj.date is None:
            return None
        return obj.date.astimezone(pytz.timezone('US/Pacific')) 

    class Meta:
        fields = ('id', 'title', 'content', 'image', 'is_html', 'created_at',)
        model = models.Blog

class BlogSnippetSerializer(serializers.ModelSerializer):

    def get_created_at(self, obj):
        if obj.date is None:
            return None
        return obj.date.astimezone(pytz.timezone('US/Pacific')) 

    class Meta:
        fields = ('id', 'title', 'snippet', 'image', 'created_at',)
        model = models.Blog        