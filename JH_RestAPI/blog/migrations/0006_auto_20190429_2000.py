# Generated by Django 2.2 on 2019-04-29 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190429_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='author_image',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='blog',
            name='author_name',
            field=models.CharField(default='JobHax', max_length=30),
        ),
    ]
