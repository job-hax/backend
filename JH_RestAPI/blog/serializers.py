from rest_framework import serializers
from . import models
import pytz
from users.serializers import ProfileSerializer


class BlogSerializer(serializers.ModelSerializer):
    publisher_profile = ProfileSerializer(read_only=True)
    upvote = serializers.SerializerMethodField()
    downvote = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        if obj.date is None:
            return None
        return obj.date.astimezone(pytz.timezone('US/Pacific'))

    def get_upvote(self, obj):
        return models.Vote.objects.filter(blog=obj, vote_type=True).count()

    def get_downvote(self, obj):
        return models.Vote.objects.filter(blog=obj, vote_type=False).count()

    def get_voted(self, obj):
        voted = 0
        user_vote = models.Vote.objects.filter(
            user=self.context.get('user'), blog=obj)
        if len(user_vote) > 0:
            if user_vote[0].vote_type:
                voted = 1
            else:
                voted = -1
        return voted

    class Meta:
        fields = ('id', 'publisher_profile', 'title', 'content', 'header_image',
                'created_at', 'view_count', 'upvote', 'downvote', 'voted', 'is_published')
        model = models.Blog


class BlogSnippetSerializer(serializers.ModelSerializer):

    upvote = serializers.SerializerMethodField()
    downvote = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        if obj.date is None:
            return None
        return obj.date.astimezone(pytz.timezone('US/Pacific'))

    def get_upvote(self, obj):
        return models.Vote.objects.filter(blog=obj, vote_type=True).count()

    def get_downvote(self, obj):
        return models.Vote.objects.filter(blog=obj, vote_type=False).count()

    def get_voted(self, obj):
        voted = 0
        user_vote = models.Vote.objects.filter(
            user=self.context.get('user'), blog=obj)
        if len(user_vote) > 0:
            if user_vote[0].vote_type:
                voted = 1
            else:
                voted = -1
        return voted

    class Meta:
        fields = ('id','publisher_profile', 'title', 'snippet',
                  'header_image', 'created_at', 'view_count', 'upvote', 'downvote', 'voted', 'is_published')
        model = models.Blog
