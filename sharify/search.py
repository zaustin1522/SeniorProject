#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Utility Methods for Music Search
###########################################################################################

#-----------------------------------------------------------------------------------------#


import json
import random

from sharify.models import Musicdata
from sharify.models import User as MyUser

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
def find_track_by_name(track):
    query = Musicdata.objects.filter(track_name__icontains = track).values('track_id')
    resp = list(query)
    # Randomize to get different results each time
    random.shuffle(resp)
    # Return the id of up to 12 songs
    songs = [item['track_id'] for item in resp[:12]]
    results = [songs[i:i+4] for i in range(0, len(songs), 4)]
    return {
	'results': results,
    'type': "track"
    }

#-----------------------------------------------------------------------------------------#
def find_album_by_name(album):
    query = Musicdata.objects.filter(album_name__icontains = album).values('album_id')
    temp = list(query)
    resp = []
    [resp.append(album) for album in temp if album not in resp]
    # Randomize to get different results each time
    random.shuffle(resp)
    # Return the id of up to 9 albums
    albums = [item['album_id'] for item in resp[:9]]
    albumGrid = [albums[i:i+3] for i in range(0, len(albums), 3)]
    return {
        'results': albumGrid,
	'type': "album"
    }

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