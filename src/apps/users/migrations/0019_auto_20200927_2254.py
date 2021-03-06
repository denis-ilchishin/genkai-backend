# Generated by Django 3.1 on 2020-09-27 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_viewedepisode_start_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='telegram_id',
            field=models.PositiveIntegerField(editable=False, null=True, verbose_name='Telegram ID'),
        ),
        migrations.AddField(
            model_name='user',
            name='vk_id',
            field=models.PositiveIntegerField(editable=False, null=True, verbose_name='VK ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, null=True, unique=True, verbose_name='email address'),
        ),
    ]
