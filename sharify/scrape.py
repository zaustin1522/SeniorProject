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
    for item in items:
        if item['track'] is not None and Musicdata.objects.filter(track_id = item['track']['id']).count() == 0:
            scrape_album(item['track']['album']['id'])

#-----------------------------------------------------------------------------------------#
def scrape_track(track: json):
    if 'album' in track:
        artist_list: list = track['album']['artists']
    else:
        artist_list: list = track['artists']
    num_artists: int = len(artist_list)
    track['available_markets'] = ""
    artist_string: str = ""
    if num_artists == 1:
        artist_string = artist_list[0]['name']
    elif num_artists == 2:
        artist_string = artist_list[0]['name'] + " & " + artist_list[1]['name']
    else:
        for artist_number in range (num_artists - 1):
            artist_string = artist_string + artist_list[artist_number]['name'] + ", "
        artist_string = artist_string + "& " + artist_list[num_artists - 1]['name']
        
    new_track: Musicdata = Musicdata.objects.create(
        track_id = track['id'],
        track_name = track['name'],
        artist = artist_string,
        popularity  = track['popularity'],
        album_id  = track['album']['id'],
        album_name = track['album']['name'],
        album_release_date = int(str(track['album']['release_date'])[:4]),
        duration_ms  = track['duration_ms'],
        image_url = track['album']['images'][0]['url']
    )
    logmessage(type = "ADD TRACK", msg = str(new_track))

#-----------------------------------------------------------------------------------------#
def scrape_album(album_id: str):
    album: json = spotipy_controller.album_tracks(album_id = album_id)
    track_ids: list = []
    track: json
    for track in album['items']:
        try:
            Musicdata.objects.get(track_id=track['id'])
        except Musicdata.DoesNotExist:
            track_ids.append(track['id'])
    if len(track_ids) > 0:
        tracks: json = spotipy_controller.tracks(tracks=track_ids)
        logmessage(type = "SCRAPE", msg = "Found some tracks to add!")
        for track in tracks['tracks']:
            scrape_track(track)
    album_liason_service(album_id)

#-----------------------------------------------------------------------------------------#
def album_liason_service(album_id: str):
    query = Musicdata.objects.filter(album_id = album_id)
    if query.filter(album_liason = True).count() == 0:
        the_one: Musicdata = query.first()
        the_one.album_liason = True
        the_one.save()
    return

#-----------------------------------------------------------------------------------------#
def update_images(tracks: list):
    if len(tracks) == 0:
        return tracks

    track_ids: list = []
    for track in tracks:
        track: Musicdata
        track_ids.append(track.track_id)

    track_json: json = spotipy_controller.tracks(tracks=track_ids)
    image_set: dict = {}
    for data in track_json['tracks']:
        image_set[data['id']] = data['album']['images'][0]['url']
    
    for track in tracks:
        if track.image_url == "":
            track.image_url = image_set[track.track_id]
            track.save()
            logmessage(type="SCRAPE", msg="Updated the image for " + str(track))
    return tracks

