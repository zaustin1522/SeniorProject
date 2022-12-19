#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Utility Methods for Music Search
###########################################################################################

#-----------------------------------------------------------------------------------------#


import json
import random
from urllib.parse import quote
import requests
from sharify.auth import get_access_token
from sharify.log import logmessage

from sharify.models import Comment, Musicdata
from sharify.models import User as MyUser
from sharify.scrape import scrape_album, scrape_track, update_images

#-----------------------------------------------------------------------------------------#
def find_albums(artist, from_year = None, to_year = None):
    query = Musicdata.objects.filter(artist__icontains = artist)
    if from_year is not None:
        query = query.filter(album_release_date__gte = from_year)
    if to_year is not None:
        query = query.filter(album_release_date__lte = to_year)
    query = query.all().order_by('album_id')
    track: Musicdata
    averagePopularity = dict()
    track = query.first()
    albumTracker = ""
    numTracks = 0
    albumPopularity = 0.0
    for track in query:
        if track.album_id == albumTracker:
            numTracks = numTracks + 1.0
            albumPopularity += track.popularity
        else:
            if numTracks != 0:
                averagePopularity[albumTracker] = albumPopularity / float(numTracks)
            albumTracker = track.album_id
            numTracks = 1
            albumPopularity = float(track.popularity)
    if numTracks != 0:
        averagePopularity[albumTracker] = albumPopularity / numTracks

    results = dict(sorted(averagePopularity.items(), key=lambda popularity: popularity[1], reverse=True))
    results = list(results)
    return results

#-----------------------------------------------------------------------------------------#
def find_track_by_name(track: str, user: MyUser):
    query = Musicdata.objects.filter(track_name__icontains = track)
    resp = list(query)
    random.shuffle(resp)
    resp = update_images(resp[:50])

    resp = resp[:12]

    if len(resp) < 12:
        if pull_more_tracks(track, 12-len(resp), user):
            query = Musicdata.objects.filter(track_name__istartswith = track)
            resp = update_images(list(query)[:50])
            # Randomize to get different results each time
            random.shuffle(resp)
            resp = resp[:12]

    songs: list = []
    for item in resp:
        comments = list(Comment.objects.filter(on_type = 'track').filter(comment_on_id = item).order_by('-posted_at'))
        songs.append((item, comments))

    # Return the id of up to 12 songs
    results = [songs[i:i+2] for i in range(0, len(songs), 2)]
    
    return results

#-----------------------------------------------------------------------------------------#
def pull_more_tracks(query: str, minimum: int, user: MyUser):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + get_access_token(user),
    }

    params = {
        'q': quote(query),
        'type': 'track',
        'market': 'US',
        'limit': 24,
    }

    response = requests.get('https://api.spotify.com/v1/search', params=params, headers=headers)

    if response.status_code != 200:
        return False
    else:
        track_json: json = json.loads(response.content)
        for track in track_json['tracks']['items']:
            try:
                Musicdata.objects.get(track_id = track['id'])
            except Musicdata.DoesNotExist:
                scrape_album(track['album']['id'])
        return True

#-----------------------------------------------------------------------------------------#
def find_album_by_name(album_name: str, user: MyUser):
    query = Musicdata.objects.filter(album_liason = True).filter(album_name__istartswith = album_name)
    resp = list(query)
    random.shuffle(resp)
    resp = resp[:12]

    if len(resp) < 12:
        logmessage(msg="Not enough albums matched.")
        if pull_more_albums(album_name, user):
            query = Musicdata.objects.filter(album_liason = True).filter(album_name__istartswith = album_name)
            resp = list(query)
            random.shuffle(resp)
            resp = resp[:12]

    albums: list = []
    for album_liason in resp:
        comments = list(Comment.objects.filter(on_type = 'album').filter(comment_on = album_liason).order_by('-posted_at'))
        albums.append((album_liason, comments))

    # Return the id of up to 12 songs
    results = [albums[i:i+2] for i in range(0, len(albums), 2)]
    return results

#-----------------------------------------------------------------------------------------#
def pull_more_albums(query: str, user: MyUser):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + get_access_token(user),
    }
    params = {
        'q': quote(query),
        'type': 'album',
        'market': 'US'
    }
    logmessage(msg="Sending request...")
    response = requests.get('https://api.spotify.com/v1/search', params=params, headers=headers)

    if response.status_code != 200:
        logmessage(msg="Pulling didn't work.")
        return False
    else:
        album_json: json = json.loads(response.content)
        for album in album_json['albums']['items']:
            if Musicdata.objects.filter(album_id = album['id']).count() == 0:
                logmessage(msg="Gotta scrape!")
                scrape_album(album['id'])
    return True


#-----------------------------------------------------------------------------------------#
def find_user_by_name(user):
    query = MyUser.objects.filter(username__icontains = user)
    resp = list(query)
    users = list()
    for another_user in resp:
        another_user: MyUser
        users.append(another_user)
    userGrid = [users[i:i+3] for i in range(0, len(users), 3)]
    return {'results': userGrid}
