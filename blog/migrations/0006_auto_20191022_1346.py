# Generated by Django 2.2 on 2019-10-22 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20191013_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
