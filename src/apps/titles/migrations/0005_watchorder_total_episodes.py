# Generated by Django 3.0.4 on 2020-06-30 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0004_auto_20200627_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchorder',
            name='total_episodes',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='общее кол-во эп.'),
        ),
    ]
