# Generated by Django 3.2.15 on 2022-12-05 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharify', '0002_user_friends_are_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='playlists_are_public',
            field=models.BooleanField(default=True),
        ),
    ]
