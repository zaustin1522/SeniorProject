# Generated by Django 3.2.15 on 2022-12-16 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharify', '0002_musicdata_artist_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musicdata',
            name='artist_ids',
            field=models.JSONField(default=list),
        ),
    ]
