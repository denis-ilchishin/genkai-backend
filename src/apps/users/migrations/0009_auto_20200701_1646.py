# Generated by Django 3.0.4 on 2020-07-01 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_notification_subscriptionnotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', related_query_name='subscription', to=settings.AUTH_USER_MODEL),
        ),
    ]
