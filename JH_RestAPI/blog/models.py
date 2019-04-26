from django.db import models
from JH_RestAPI import settings
from django.contrib.auth import get_user_model

class Blog(models.Model):
    title = models.CharField(max_length=50)
    snippet = models.CharField(null=True,max_length=150)
    is_html = models.BooleanField(default=False)
    image = models.CharField(null=True, max_length=200)
    view_count = models.IntegerField(default=0)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Vote(models.Model):
    User = get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_user')    
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)  
    vote_type = models.BooleanField(default=False)
