# Generated by Django 2.2 on 2019-08-07 08:37

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('web_pages',
                 django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True, null=True),
                                                           size=None)),
                ('domains',
                 django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True, null=True),
                                                           size=None)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('alpha_two_code', models.CharField(blank=True, max_length=5)),
                ('state_province', models.CharField(blank=True, max_length=30, null=True)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('supported', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]