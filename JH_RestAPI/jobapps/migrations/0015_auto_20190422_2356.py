# Generated by Django 2.1.5 on 2019-04-22 23:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('jobapps', '0014_prepopulate_company_and_position_tables'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobapplication',
            name='company',
        ),
        migrations.RemoveField(
            model_name='jobapplication',
            name='companyLogo',
        ),
        migrations.RemoveField(
            model_name='jobapplication',
            name='jobTitle',
        ),
    ]
