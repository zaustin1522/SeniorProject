# Generated by Django 3.2.15 on 2022-12-08 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharify', '0004_comment_on_album'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='on_album',
        ),
        migrations.AddField(
            model_name='musicdata',
            name='album_liason',
            field=models.BooleanField(default=False),
        ),
    ]