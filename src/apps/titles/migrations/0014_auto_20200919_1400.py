# Generated by Django 3.1 on 2020-09-19 06:00

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20200901_1700'),
        ('titles', '0013_auto_20200919_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='age_rating',
            field=models.CharField(blank=True, choices=[('G', 'G — нет возрастных ограничений'), ('PG', 'PG — рекомендуется присутствие родителей'), ('PG-13', 'PG-13 — не желателен к просмотру до 13 лет'), ('R', 'R — до 17 лет к просмотру только в присутствии родителей'), ('NC-17', 'NC-17 — до 17 лет к просмотру запрещен')], db_index=True, max_length=10, null=True, verbose_name='возрастной рейтинг'),
        ),
        migrations.AlterField(
            model_name='title',
            name='characters',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None, verbose_name='персонажи'),
        ),
        migrations.AlterField(
            model_name='title',
            name='countries',
            field=models.ManyToManyField(blank=True, to='content.Country', verbose_name='страны'),
        ),
        migrations.AlterField(
            model_name='title',
            name='duration',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='длительность эпизода'),
        ),
        migrations.AlterField(
            model_name='title',
            name='genres',
            field=models.ManyToManyField(blank=True, to='content.Genre', verbose_name='жанры'),
        ),
        migrations.AlterField(
            model_name='title',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='title',
            name='other_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None, verbose_name='другие названия'),
        ),
        migrations.AlterField(
            model_name='title',
            name='release_day',
            field=models.CharField(blank=True, choices=[('mon', 'понедельник'), ('tue', 'вторник'), ('wed', 'среда'), ('thu', 'четверг'), ('fri', 'пятница'), ('sat', 'суббота'), ('sun', 'воскресенье')], max_length=3, null=True, verbose_name='день недели выхода серий'),
        ),
        migrations.AlterField(
            model_name='title',
            name='source',
            field=models.CharField(blank=True, choices=[('manga', 'манга'), ('manhwa', 'манхва'), ('game', 'игра'), ('novel', 'ранобэ'), ('original', 'оригинальная идея'), ('book', 'книга')], max_length=10, null=True, verbose_name='первоисточник'),
        ),
        migrations.AlterField(
            model_name='title',
            name='status',
            field=models.CharField(choices=[('released', 'завершенный'), ('ongoing', 'онгоинг'), ('announce', 'анонс')], db_index=True, max_length=10, null=True, verbose_name='статус'),
        ),
        migrations.AlterField(
            model_name='title',
            name='studios',
            field=models.ManyToManyField(blank=True, to='content.Studio', verbose_name='студии'),
        ),
        migrations.AlterField(
            model_name='title',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None, verbose_name='тэги'),
        ),
        migrations.AlterField(
            model_name='title',
            name='total_episodes',
            field=models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='общее кол-во эп.'),
        ),
        migrations.AlterField(
            model_name='title',
            name='type',
            field=models.CharField(blank=True, choices=[('series', 'TV сериал'), ('movie', 'п/ф'), ('ova', 'OVA'), ('ona', 'ONA'), ('special', 'спешл')], db_index=True, max_length=10, null=True, verbose_name='тип'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2100), django.core.validators.MinValueValidator(1900)], verbose_name='год выхода'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year_season',
            field=models.CharField(blank=True, choices=[('winter', 'зима'), ('spring', 'весна'), ('summer', 'лето'), ('autumn', 'осень')], db_index=True, max_length=10, null=True, verbose_name='сезон года'),
        ),
        migrations.AlterField(
            model_name='watchorder',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='watchorder',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='watchorder',
            name='title',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='titles.title', verbose_name='тайтл'),
        ),
        migrations.AlterField(
            model_name='watchorder',
            name='total_episodes',
            field=models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='общее кол-во эп.'),
        ),
        migrations.AlterField(
            model_name='watchorder',
            name='type',
            field=models.CharField(blank=True, choices=[('series', 'TV сериал'), ('movie', 'п/ф'), ('ova', 'OVA'), ('ona', 'ONA'), ('special', 'спешл')], db_index=True, max_length=10, null=True, verbose_name='тип'),
        ),
        migrations.AlterField(
            model_name='watchorder',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2100), django.core.validators.MinValueValidator(1900)], verbose_name='год выхода'),
        ),
    ]
