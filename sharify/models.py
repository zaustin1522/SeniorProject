from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class Musicdata(models.Model):
    track_id = models.TextField()
    track_name = models.TextField()
    track_artist = models.TextField()
    track_popularity  = models.FloatField()
    track_album_id  = models.TextField()
    track_album_name = models.TextField()
    track_album_release_date = models.IntegerField()
    playlist_name = models.TextField()
    playlist_id = models.TextField()
    playlist_genre = models.TextField()
    playlist_subgenre = models.TextField()
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.FloatField()
    loudness = models.FloatField()
    mode = models.FloatField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    duration_ms  = models.IntegerField()

class User(AbstractUser):
    pass
    def __str__(self):
        return self.username
    user_dob = models.DateTimeField(blank=True, default=datetime.now)
    user_bio = models.TextField(blank=True, default="")
    user_avatar = models.ImageField(blank=True, default="")
    user_id = models.AutoField(primary_key=True)
    user_is_paired = models.BooleanField(default=False)
    user_spotify_id = models.CharField(max_length=50, blank=True, null=True)
    user_spotify_fav_artist = models.CharField(max_length=50, blank=True, null=True)
    user_spotify_friends = models.TextField(blank=True, null=True)
