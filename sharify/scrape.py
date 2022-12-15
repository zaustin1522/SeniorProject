#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Method for Playlist and Song Scraping
###########################################################################################

#-----------------------------------------------------------------------------------------#


from sharify.auth import *
from sharify.log import *
from sharify.models import Musicdata


#-----------------------------------------------------------------------------------------#
def scrape_playlist(items: json):
    global global_current_user
    for item in items:
        if item['track'] is not None and Musicdata.objects.filter(track_id = item['track']['id']).count() == 0:
            global_current_user = MyUser.objects.get(id=7)
            scrape_track(item['track'])

#-----------------------------------------------------------------------------------------#
def scrape_track(track: json):
    num_artists: int = len(track['artists'])
    track['available_markets'] = ""
    artist_string: str = ""
    if num_artists == 1:
        artist_string = track['artists'][0]['name']
    elif num_artists == 2:
        artist_string = track['artists'][0]['name'] + " & " + track['artists'][1]['name']
    else:
        for artist_number in range (num_artists - 1):
            artist_string = artist_string + track['artists'][artist_number]['name'] + ", "
        artist_string = artist_string + "& " + track['artists'][num_artists - 1]['name']
        
    new_track = Musicdata.objects.create(
        track_id = track['id'],
        track_name = track['name'],
        artist = artist_string,
        popularity  = track['popularity'],
        album_id  = track['album']['id'],
        album_name = track['album']['name'],
        album_release_date = int(str(track['album']['release_date'])[:4]),
        duration_ms  = track['duration_ms']
    )
    new_track.save()
    logmessage(type = "ADD TRACK", msg = str(new_track))

#-----------------------------------------------------------------------------------------#
def scrape_album(album_id: str):
    global global_current_user
    album: json = spotipy_controller.album_tracks(album_id = album_id)
    track_ids: list = []
    track: json
    for track in album['items']:
        if Musicdata.objects.filter(track_id=track['id']).count() == 0:
            track_ids.append(track['id'])
    tracks: json = spotipy_controller.tracks(tracks=track_ids)
    logmessage(type = "ALBUM SCRAPE", msg = str(global_current_user) + " found some tracks to add!")
    for track in tracks['tracks']:
        scrape_track(track)
