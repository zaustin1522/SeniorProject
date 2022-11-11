from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Musicdata(models.Model):
    id = models.AutoField(primary_key = True)
    track_id = models.TextField()
    track_name = models.TextField()
    artist = models.TextField()
    popularity  = models.FloatField()
    album_id  = models.TextField()
    album_name = models.TextField()
    album_release_date = models.IntegerField()
    duration_ms  = models.IntegerField()

    def __str__(self):
        return "\"" + self.track_name + "\" by " + self.track_artist

    class Meta: 
        ordering = ('artist', 'album_name', 'track_name',) 

class SpotifyProfile(models.Model):
    display_name = models.TextField(default = "")       # ['display_name']
    spotify_id = models.TextField(default = "")         # ['id']
    follower_total = models.IntegerField(default = 0)   # ['followers']['total']
    api_access = models.TextField(default = "")         # ['href']
    avatar_url = models.TextField(default = "")         # ['images'][0]['url']
    token_info = models.JSONField(default = "")         # Full token object, get_access_token

    def __str__(self):
        return self.spotify_id

class User(AbstractUser):
    dob = models.DateTimeField(blank=True, null=True)
    bio = models.TextField(default="")
    id = models.AutoField(primary_key=True)
    fav_artist = models.CharField(max_length=50, blank=True, null=True)
    friends = models.ManyToManyField("self")
    pending_requests_out = models.ManyToManyField("self", symmetrical=False)
    pending_requests_in = models.ManyToManyField("self", symmetrical=False)
    profile = models.OneToOneField(SpotifyProfile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username

class Playlist(models.Model):
    id = models.CharField(max_length=120, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    spotify_id = models.CharField(max_length=120, default="null")
    name = models.TextField(max_length=100)
    url = models.CharField(max_length=1000)
    num_tracks = models.IntegerField(null=True)
    featured = models.BooleanField(default=False)
    genre = models.CharField(max_length=100)
    date_created = models.CharField(max_length=500, default="No date")
    image = models.ImageField(blank=True, default="")
    songs = models.ManyToManyField(Musicdata)

    def __str__(self):
        return self.name

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    posted_at = models.DateTimeField(default = timezone.now)
    comment_on = models.ForeignKey(Musicdata, on_delete = models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete = models.DO_NOTHING)
    comment = models.TextField(default = "")

    class Meta: 
        ordering = ('comment_on', 'posted_at',) 

    def __str__(self): 
        return '{}: {}'.format(self.user.username, self.comment)
