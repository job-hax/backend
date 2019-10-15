from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.postgres.fields import JSONField


class College(models.Model):
    web_pages = ArrayField(models.TextField(null=True, blank=True))
    domains = ArrayField(models.TextField(null=True, blank=True))
    name = models.CharField(max_length=200, blank=False)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    alpha_two_code = models.CharField(max_length=5, blank=True)
    state_province = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=50, blank=True)
    supported = models.BooleanField(default=False)
    jobhax_domain = models.CharField(max_length=30, blank=True, null=True)
    jobhax_subdomain = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name if self.name is not None else ''


class CollegeCoach(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=False, blank=False)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    profile_photo = models.FileField(blank=False, null=False)
    summary_photo = models.FileField(blank=False, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField(null=False, blank=False)
    calendar_link = models.CharField(max_length=150, null=False, blank=False)
    online_conference_link = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_publish = models.BooleanField(default=False)


class HomePage(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=False, blank=False)
    header_banners = JSONField(null=True, blank=True)
    additional_banners = JSONField(null=True, blank=True)
    social_media_accounts = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class HomePageVideo(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=False, blank=False)
    embed_code = models.CharField(max_length=300, null=False, blank=False)
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_publish = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class LandingPage(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=False, blank=False)
    fields = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)