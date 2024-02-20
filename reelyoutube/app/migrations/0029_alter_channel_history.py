# Generated by Django 3.2.7 on 2022-11-04 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_channel_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='history',
            field=models.ManyToManyField(blank=True, null=True, related_name='history_user', to='app.Video'),
        ),
    ]
