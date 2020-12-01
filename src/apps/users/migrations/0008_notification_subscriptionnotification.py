# Generated by Django 3.0.4 on 2020-06-27 06:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0002_auto_20200616_1553'),
        ('users', '0007_usersubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'подписка')])),
                ('seen', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='SubscriptionNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.Notification')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='translations.Episode')),
            ],
            options={
                'abstract': False,
            },
            bases=('users.notification',),
        ),
    ]