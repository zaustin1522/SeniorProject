from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Musicdata(models.Model):
    track_id = models.TextField(primary_key=True)
    id = models.IntegerField(null=True, blank=True)
    track_name = models.TextField()
    image_url = models.TextField(default="")
    artist = models.TextField()
    popularity  = models.FloatField()
    album_id  = models.TextField()
    album_name = models.TextField()
    album_release_date = models.IntegerField()
    duration_ms  = models.IntegerField()

    def __str__(self):
        return "\"" + self.track_name + "\" by " + self.artist

    class Meta: 
        ordering = ('artist', 'album_name', 'track_name',) 

class SpotifyProfile(models.Model):
    id = models.AutoField(primary_key=True)
    display_name = models.TextField(default = "")           # ['display_name']
    spotify_id = models.TextField(default = "")             # ['id']
    follower_total = models.IntegerField(default = 0)       # ['followers']['total']
    api_access = models.TextField(default = "")             # ['href']
    avatar_url = models.TextField(default = "")             # ['images'][0]['url']
    token_info = models.JSONField(default = dict)           # Full token object, get_access_token

    def __str__(self):
        return self.spotify_id

class User(AbstractUser):
    def __str__(self):
        return self.username

    def pending_default():
        return {"in": [], "out": []}
        
    dob = models.DateTimeField(blank=True, null=True)
    bio = models.TextField(default="")
    id = models.AutoField(primary_key=True)
    friends_are_public = models.BooleanField(default=True, blank=False, null=False)
    playlists_are_public = models.BooleanField(default=True, blank=False, null=False)
    friends = models.JSONField(default=list)
    pending = models.JSONField(default=pending_default)
    profile = models.OneToOneField(SpotifyProfile, on_delete=models.CASCADE, null=True, blank=True)


class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.TextField(max_length=100)
    date_created = models.DateTimeField(default = timezone.now)
    songs = models.ManyToManyField(Musicdata)

    def __str__(self):
        return self.name

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    posted_at = models.DateTimeField(default = timezone.now)
    comment_on = models.ForeignKey(Musicdata, on_delete = models.DO_NOTHING, db_constraint=False)
    user = models.ForeignKey(User, on_delete = models.DO_NOTHING)
    comment = models.TextField(default = "")

    class Meta: 
        ordering = ('comment_on', 'posted_at',) 

    def __str__(self): 
        return "{}: {}".format(self.user.username, self.comment)
