from django.contrib.auth import get_user_model
from django.db import models


class Blog(models.Model):
    publisher_profile = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    snippet = models.CharField(null=True, blank=True, max_length=400)
    header_image = models.FileField(blank=True, null=True)
    view_count = models.IntegerField(default=0)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    is_publish = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        if self.title is None:
            return ''
        return self.title

    class Meta:
        ordering = ['-created_at']


class Vote(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='vote_user')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    vote_type = models.BooleanField(default=False)
