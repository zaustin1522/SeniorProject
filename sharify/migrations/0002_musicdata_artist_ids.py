# Generated by Django 3.2.15 on 2022-12-16 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicdata',
            name='artist_ids',
            field=models.TextField(default=list),
        ),
    ]
