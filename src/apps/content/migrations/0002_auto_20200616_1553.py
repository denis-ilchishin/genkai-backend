# Generated by Django 3.0.4 on 2020-06-16 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='_active',
        ),
        migrations.RemoveField(
            model_name='genre',
            name='_active',
        ),
        migrations.RemoveField(
            model_name='studio',
            name='_active',
        ),
    ]
