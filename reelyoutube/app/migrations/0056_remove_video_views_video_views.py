# Generated by Django 4.1.7 on 2023-08-13 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0055_video_gif'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='views',
        ),
        migrations.AddField(
            model_name='video',
            name='views',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]