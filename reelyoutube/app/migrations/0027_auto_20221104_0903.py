# Generated by Django 3.2.7 on 2022-11-04 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_video_watchlater'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='facebook_url',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='instagram_url',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='twitter_url',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
    ]