# Generated by Django 2.2 on 2019-05-28 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20190517_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='synching',
            field=models.BooleanField(default=False),
        ),
    ]
