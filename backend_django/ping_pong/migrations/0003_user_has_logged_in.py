# Generated by Django 3.2.25 on 2024-03-06 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ping_pong', '0002_friendship'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_logged_in',
            field=models.BooleanField(default=False),
        ),
    ]
