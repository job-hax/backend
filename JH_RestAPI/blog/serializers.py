from rest_framework import serializers
from . import models
import pytz


class BlogSerializer(serializers.ModelSerializer):

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
        user_vote = models.Vote.objects.filter(user=self.context.get('user'), blog=obj)
        if len(user_vote) > 0:
            if user_vote[0].vote_type:
                voted = 1
            else:
                voted = -1
        return voted              

    class Meta:
        fields = ('id', 'title', 'author_name', 'author_image', 'content', 'image', 'is_html', 'created_at', 'view_count', 'upvote', 'downvote', 'voted')
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
        user_vote = models.Vote.objects.filter(user=self.context.get('user'), blog=obj)
        if len(user_vote) > 0:
            if user_vote[0].vote_type:
                voted = 1
            else:
                voted = -1
        return voted        

    class Meta:
        fields = ('id', 'title', 'author_name', 'author_image', 'snippet', 'image', 'created_at', 'view_count', 'upvote', 'downvote', 'voted')
        model = models.Blog        