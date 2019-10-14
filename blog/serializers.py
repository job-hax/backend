import pytz
from rest_framework import serializers
from bs4 import BeautifulSoup as bs

from users.serializers import UserSerializer, UserTypeSerializer
from . import models


class BlogSerializer(serializers.ModelSerializer):
    publisher_profile = UserSerializer(read_only=True)
    upvote = serializers.SerializerMethodField()
    downvote = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()
    word_count = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    user_types = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BlogSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('user')
        if user.user_type.name != 'Career Service':
            del self.fields['user_types']

    def get_user_types(self, obj):
        if self.context.get('user').user_type.name == 'Career Service':
            return UserTypeSerializer(instance=obj.user_types, context={'basic': True}, many=True).data

    def get_mine(self, obj):
        return obj.publisher_profile == self.context.get('user')

    def get_word_count(self, obj):
        if obj.content:
            line_soup = bs(obj.content.strip(), 'html.parser')
            # naive way to get words count
            words_count = len(line_soup.text.split())
            return words_count
        return 0

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
        fields = ('id', 'publisher_profile', 'mine', 'title', 'content', 'header_image', 'snippet', 'user_types',
                  'created_at', 'updated_at', 'view_count', 'upvote', 'downvote', 'word_count', 'voted', 'is_publish',
                  'is_approved')
        model = models.Blog


class BlogSnippetSerializer(serializers.ModelSerializer):
    publisher_profile = UserSerializer(read_only=True)
    upvote = serializers.SerializerMethodField()
    downvote = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()
    word_count = serializers.SerializerMethodField()
    user_types = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BlogSnippetSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('user')
        if user.user_type.name != 'Career Service':
            del self.fields['user_types']

    def get_user_types(self, obj):
        if self.context.get('user').user_type.name == 'Career Service':
            return UserTypeSerializer(instance=obj.user_types, context={'basic': True}, many=True).data

    def get_word_count(self, obj):
        if obj.content:
            line_soup = bs(obj.content.strip(), 'html.parser')
            # naive way to get words count
            words_count = len(line_soup.text.split())
            return words_count
        return 0

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
        fields = ('id', 'publisher_profile', 'title', 'snippet', 'user_types',
                  'header_image', 'created_at', 'updated_at', 'view_count', 'upvote', 'downvote', 'word_count', 'voted',
                  'is_publish', 'is_approved')
        model = models.Blog
