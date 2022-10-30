from django.db import models
from django.contrib.auth.models import AbstractUser

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
#    name = models.CharField(max_length=50, default="user")
#    username = models.CharField(max_length=50, default="user")
#    dateOfBirth = models.DateTimeField()
#    email = models.EmailField(max_length=254)
#    biography = models.TextField()
#    profilePicture = models.ImageField()
#    spotifyUserID = models.CharField(max_length=50)
#    spotifyFavArtist = models.CharField(max_length=50)
#    spotifyFriendList = models.TextField()

