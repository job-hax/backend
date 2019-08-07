# Generated by Django 2.2 on 2019-05-01 23:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('review', '0007_auto_20190501_0453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='interview_difficulty',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(5),
                                                                         django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='overall_interview_experience',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1),
                                                                         django.core.validators.MinValueValidator(0)]),
        ),
    ]
