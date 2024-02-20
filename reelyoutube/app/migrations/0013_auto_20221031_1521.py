# Generated by Django 3.2.7 on 2022-10-31 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_history_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='video',
        ),
        migrations.AddField(
            model_name='history',
            name='video',
            field=models.ManyToManyField(blank=True, null=True, related_name='videohistory', to='app.Video'),
        ),
    ]
