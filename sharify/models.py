from django.db import models

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


class Playlist(models.Model):
    playlist_id = models.CharField(max_length=120, primary_key=True)
    playlist_name = models.TextField(max_length=100)
    playlist_url = models.CharField(max_length=1000)
    playlist_num_tracks = models.IntegerField(null=True)
    playlist_featured = models.BooleanField(default=False)
    playlist_genre = models.CharField(max_length=100)
    playlist_owner = models.CharField(max_length=500)
    date_created = models.CharField(max_length=500, default="No date")
    playlist_img = models.ImageField(blank=True, default="")
    songs = models.OneToMany(Musicdata)

    def __str__(self):
        return self.playlist_name
