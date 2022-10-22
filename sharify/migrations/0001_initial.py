# Generated by Django 3.2.15 on 2022-10-22 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Musicdata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_id', models.TextField()),
                ('track_name', models.TextField()),
                ('track_artist', models.TextField()),
                ('track_popularity', models.FloatField()),
                ('track_album_id', models.TextField()),
                ('track_album_name', models.TextField()),
                ('track_album_release_date', models.IntegerField()),
                ('playlist_name', models.TextField()),
                ('playlist_id', models.TextField()),
                ('playlist_genre', models.TextField()),
                ('playlist_subgenre', models.TextField()),
                ('danceability', models.FloatField()),
                ('energy', models.FloatField()),
                ('key', models.FloatField()),
                ('loudness', models.FloatField()),
                ('mode', models.FloatField()),
                ('speechiness', models.FloatField()),
                ('acousticness', models.FloatField()),
                ('instrumentalness', models.FloatField()),
                ('liveness', models.FloatField()),
                ('valence', models.FloatField()),
                ('tempo', models.FloatField()),
                ('duration_ms', models.IntegerField()),
            ],
        ),
    ]
