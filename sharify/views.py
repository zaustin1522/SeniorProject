###########################################################################################
#   Imports
###########################################################################################
import json
import random

import spotipy
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from sharify.forms import SearchForm

from .forms import *
from .models import Musicdata, SpotifyProfile
from .models import User as MyUser

###########################################################################################
#   Loading Environment and Setting Spotify Controller
###########################################################################################
load_dotenv()

# Instantiating the Spotipy unauthenticated controller
spotipy_controller = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
# Scope for Token (Privileges)
scope = [
    'ugc-image-upload',
    'user-read-playback-state',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'streaming',
    'playlist-read-private',
    'playlist-read-collaborative',
    'playlist-modify-private',
    'playlist-modify-public',
    'user-follow-modify',
    'user-follow-read',
    'user-read-playback-position',
    'user-top-read',
    'user-read-recently-played',
    'user-library-modify',
    'user-library-read',
    'user-read-email',
    'user-read-private']
# Sets scope for SpotifyOAuth oject so it knows what privileges we're requesting for login.
auth_manager = SpotifyOAuth(scope=scope)



#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Basic Views
###########################################################################################

#-----------------------------------------------------------------------------------------#
def homepage(request):
    return render(request, 'home.html', {})

#-----------------------------------------------------------------------------------------#
class SignUpView(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views for Authorization
###########################################################################################

#-----------------------------------------------------------------------------------------#
def link_spotify(request: WSGIRequest):
    if request.GET.get('code'):
        user: MyUser = request.user
        profile: SpotifyProfile = user.profile
        token_info: json = auth_manager.get_access_token(request.GET.get('code'))
        # if user hasn't linked before
        if profile is None:
            spotify_auth_controller = spotipy.Spotify(auth=token_info['access_token'])
            user_profile: json = spotify_auth_controller.current_user()
            display_name = user_profile['display_name']
            spotify_id = user_profile['id']
            follower_total = user_profile['followers']['total']
            api_access = user_profile['href']
            avatar_url = user_profile['images'][0]['url']
            user.profile = SpotifyProfile.objects.create(
                display_name = display_name, 
                spotify_id = spotify_id, 
                follower_total = follower_total, 
                api_access = api_access, 
                avatar_url = avatar_url, 
                token_info = token_info
            )
            user.save()
        return redirect('/userprofile/')        # Redirect to User Profile.
    # If that all failed, get authorization from Spotify
    return HttpResponseRedirect(auth_manager.get_authorize_url())

#-----------------------------------------------------------------------------------------#
# We can probably get rid of this.
def oauth_use_template(request: WSGIRequest):
    if request.user.is_authenticated:
        user: MyUser = request.user
        profile: SpotifyProfile = user.profile
        if not profile.token_info is None:
            spotify_oauth = SpotifyOAuth()
            token_info = spotify_oauth.get_access_token(profile.token_info['refresh_token'])  # Attempts to pull access token.
            if token_info:
                spotify_auth_controller = spotipy.Spotify(auth=token_info['access_token'])        # Instantiate Spotify Controller for API calls
                print(spotify_auth_controller.current_user())           # Print Current User
    return render(request, 'home.html')

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Utility Methods for Music Search
###########################################################################################

#-----------------------------------------------------------------------------------------#
def find_albums(artist, from_year = None, to_year = None):
    query = Musicdata.objects.filter(track_artist__contains = artist)
    if from_year is not None:
        query = query.filter(track_album_release_date__gte = from_year)
    if to_year is not None:
        query = query.filter(track_album_release_date__lte = to_year)
    query = query.all().order_by('track_album_id')
    track: Musicdata
    averagePopularity = dict()
    track = query.first()
    albumTracker = ""
    numTracks = 0
    albumPopularity = 0.0
    for track in query:
        if track.track_album_id == albumTracker:
            numTracks = numTracks + 1.0
            albumPopularity += track.track_popularity
        else:
            if numTracks != 0:
                averagePopularity[albumTracker] = albumPopularity / float(numTracks)
            albumTracker = track.track_album_id
            numTracks = 1
            albumPopularity = float(track.track_popularity)
    if numTracks != 0:
        averagePopularity[albumTracker] = albumPopularity / numTracks

    results = dict(sorted(averagePopularity.items(), key=lambda popularity: popularity[1], reverse=True))
    results = list(results)
    return results

#-----------------------------------------------------------------------------------------#
def find_track_by_name(track):
    query = Musicdata.objects.filter(track_name__contains = track).values('track_id')
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
    query = Musicdata.objects.filter(track_album_name__contains = album).values('track_album_id')
    temp = list(query)
    resp = []
    [resp.append(album) for album in temp if album not in resp]
    # Randomize to get different results each time
    random.shuffle(resp)
    # Return the id of up to 9 albums
    albums = [item['track_album_id'] for item in resp[:9]]
    albumGrid = [albums[i:i+3] for i in range(0, len(albums), 3)]
    return {
        'results': albumGrid,
	'type': "album"
    }

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views for Music Search and Browse
###########################################################################################

#-----------------------------------------------------------------------------------------#
def todays_top_hits(request: WSGIRequest):
    tracks = []
    # Grabs the playlist items object and grabs dict key 'items' to get an array of tracks
    for item in spotipy_controller.playlist_items(playlist_id='37i9dQZF1DXcBWIGoYBM5M')['items']:
        tracks.append(item['track']['id'])
    context = {
        # Splits first 10 tracks
        'tracks': tracks[:10]
    }
    return render(request, 'todays_top_hits.html', context)

#-----------------------------------------------------------------------------------------#
def get_artist(request: WSGIRequest):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            from_year = None if form.cleaned_data['from_year'] == None else int(form.cleaned_data['from_year'])
            to_year = None if form.cleaned_data['to_year'] == None else int(form.cleaned_data['to_year'])
            albums = find_albums(
                    form.cleaned_data['artist'],
                    from_year,
                    to_year
                )

            answer = albums[:9]
            albumGrid = [answer[i:i+3] for i in range(0, len(answer), 3)]
            return render(request, 'artist.html', {
                'form': form,
                'results': albumGrid,
                'type': "album"
            })
        else:
            raise Http404('Something went wrong')
    else:
        form = SearchForm()
        return render(request, 'artist.html', {'form': form})

#-----------------------------------------------------------------------------------------#
def get_album(request: WSGIRequest):
    if request.method == 'GET':
        album = request.GET.get('album', None)
        if album is None:
            return render(request, "album.html", {})
        else:
            albums = {}
            if album != "":
                albums = find_album_by_name(album)
            return render(request, "results.html", albums)

#-----------------------------------------------------------------------------------------#
def get_track(request: WSGIRequest):
    if request.method == 'GET':
        track = request.GET.get('track', None)
        if track is None:
            return render(request, "track.html", {})
        else:
            tracks = {}
            if track != "":
                tracks = find_track_by_name(track)
            return render(request, "results.html", tracks)

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views and Methods for Users and Profile Browsing
###########################################################################################

#-----------------------------------------------------------------------------------------#
def show_userprofile(request: WSGIRequest):
    username = request.GET.get('username')
    print(username)
    if username is None:
        return show_profile_for(request, request.user)
    findUser: MyUser = User.objects.filter(username = username).first()
    if findUser is None:
        print("fuck")
        return show_profile_for(request, request.user)
    return show_profile_for(request, findUser)

#-----------------------------------------------------------------------------------------#
def show_profile_for(request: WSGIRequest, current_user: MyUser):

    # No user is logged in, no user was requested; go to homepage
    if current_user.username == '':
        return redirect('/')

    profile: SpotifyProfile = current_user.profile

    # User does not have a linked Spotify Profile
    if profile is None:
        needs_linking = current_user != request.user
        return render(request, 'userprofile.html', {
            'current_user': current_user,
            'needs_linking': needs_linking,
            'message': current_user.username + " hasn't linked Spotify!",
            'fav_artist': "What IS art, really?"
        }) 

    # Check if User's access token is expired, and refresh it if needed.
    if auth_manager.is_token_expired(profile.token_info):
        auth_manager.refresh_access_token(refresh_token = profile.token_info['refresh_token'])
        profile.token_info['access_token'] = auth_manager.get_access_token() 
        profile.save()
    
    # Get the User's most-played artist from Spotify.
    fav_artist_data: json = spotipy_controller.current_user_top_artists()
    if fav_artist_data is not None and 'items' in fav_artist_data:
        fav_artist: str = fav_artist_data['items'][0]['name']
    else:
        fav_artist: str = current_user.username + " doesn't play favorites."

    # Get the User's most-played song from Spotify.
    fav_track_data: json = spotipy_controller.current_user_top_tracks()
    if fav_track_data is not None and 'items' in fav_track_data:
        fav_track: str = "\"" + fav_track_data['items'][0]['name'] + "\" by " + fav_track_data['items'][0]['artists'][0]['name']
    else:
        # haha, high level humor
        fav_track: str = "4'33\" by John Cage"

    current_track_data: json = spotipy_controller.currently_playing()

    # User is linked to Spotify AND is currently listening to something.
    if current_track_data is not None:
        # this might fail if the User is experiencing a Spotify ad.
        if 'item' in current_track_data:
            if 'currently_playing_type' in current_track_data:
                if not current_track_data['currently_playing_type'] == 'ad':
                    current_track_name = current_track_data['item']['name']
                    current_track_artist = current_track_data['item']['artists'][0]['name']
                    return render(request, 'userprofile.html', {
                        'current_user': current_user,
                        'listening': True,
                        'current_track_name': current_track_name,
                        'current_track_artist': current_track_artist,
                        'fav_artist': fav_artist,
                        'fav_track': fav_track
                    })
                else:
                    return render(request, 'userprofile.html', {
                        'current_user': current_user,
                        'listening': False,
                        'message': "An ad!",
                        'fav_artist': fav_artist,
                        'fav_track': fav_track
                    })
    # User is linked to Spotify, but isn't listening to anything.
    return render(request, 'userprofile.html', {
        'current_user': current_user,
        'listening': False,
        'message': "Nothing right now!",
        'fav_artist': fav_artist,
        'fav_track': fav_track
    })

#-----------------------------------------------------------------------------------------#

class UpdateUserView(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'edit_profile.html'
    success_url: reverse_lazy('home')

    def get_object(self):
        return self.request.user