# Generated by Django 4.1.7 on 2023-08-20 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0064_shorts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shorts',
            name='short_video',
            field=models.FileField(null=True, upload_to='shorts'),
        ),
    ]
