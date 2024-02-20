# Generated by Django 3.2.7 on 2022-11-04 05:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0027_auto_20221104_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='history',
            field=models.ManyToManyField(blank=True, null=True, related_name='history_user', to=settings.AUTH_USER_MODEL),
        ),
    ]