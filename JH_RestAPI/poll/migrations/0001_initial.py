# Generated by Django 2.1.5 on 2019-04-19 04:06

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=250, verbose_name='value')),
                ('pos', models.SmallIntegerField(default='0', verbose_name='position')),
            ],
            options={
                'verbose_name': 'answer',
                'verbose_name_plural': 'answers',
                'ordering': ['pos'],
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='question')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='date')),
                ('is_published', models.BooleanField(default=True, verbose_name='is published')),
            ],
            options={
                'verbose_name': 'poll',
                'verbose_name_plural': 'polls',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(verbose_name="user's IP")),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('item',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='poll.Item',
                                   verbose_name='voted item')),
                ('poll',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.Poll', verbose_name='poll')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                           to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'vote',
                'verbose_name_plural': 'votes',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='poll.Poll'),
        ),
    ]
