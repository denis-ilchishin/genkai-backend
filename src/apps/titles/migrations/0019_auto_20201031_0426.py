# Generated by Django 3.1 on 2020-10-31 04:26

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0018_remove_titlewatchorder_titles'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WatchOrder',
            new_name='WatchOrderItem',
        ),
        migrations.RenameModel(
            old_name='TitleWatchOrder',
            new_name='WatchOrderList',
        ),
    ]
