# Generated by Django 3.2.7 on 2022-11-02 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]
