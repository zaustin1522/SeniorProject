# Generated by Django 3.2.15 on 2022-12-08 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharify', '0003_comment_on_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='on_album',
            field=models.TextField(default='oops!'),
        ),
    ]