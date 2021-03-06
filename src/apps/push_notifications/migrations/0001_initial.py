# Generated by Django 3.0.4 on 2020-08-02 06:29

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotificationSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Обьект подписки')),
                ('device', models.CharField(blank=True, max_length=255, null=True, verbose_name='Устройство')),
                ('date_subscribed', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
