# Generated by Django 2.2 on 2019-05-02 00:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0011_auto_20190501_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_updated',
            field=models.BooleanField(default=False),
        ),
    ]