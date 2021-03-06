# Generated by Django 3.0.4 on 2020-08-08 05:04

from django.db import migrations, models

from ..models import Title as TitleModel

movie_type = 2


def update_titles_movies(apps, schema_editor):
    Title = apps.get_model('titles', 'Title')
    db_alias = schema_editor.connection.alias
    Title.objects.using(db_alias).filter(type=movie_type).update(season=None)


def update_titles_movies___reverse(apps, schema_editor):
    Title = apps.get_model('titles', 'Title')
    db_alias = schema_editor.connection.alias
    Title.objects.using(db_alias).filter(type=movie_type).update(season=0)


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0009_auto_20200706_0533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='season',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.operations.RunPython(
            update_titles_movies, update_titles_movies___reverse
        ),
    ]
