###########################################################################################
#   Imports
###########################################################################################
from sharify.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import Musicdata, User
from .forms import *
import random
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
import requests

User = get_user_model()

###########################################################################################
#   Loading Environment and Setting Spotify Controller
###########################################################################################
load_dotenv()

# Instantiating the Spotipy unauthenticated controller
spotipy_controller = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

#-----------------------------------------------------------------------------------------#
def todays_top_hits(request):
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
def get_artist(request):
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
def get_album(request):
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
def get_track(request):
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
def homepage(request):
    return render(request, 'home.html', {})

#-----------------------------------------------------------------------------------------#
def show_userprofile(request):
    username = request.GET.get('user')
    if username is None:
        return show_profile_for(request, request.user)
    findUser = User.objects.filter(username = username).first()
    if findUser is None:
        return show_profile_for(request, request.user)
    return show_profile_for(request, findUser)

#-----------------------------------------------------------------------------------------#
def show_profile_for(request, current_user):
    if current_user == request.user and not current_user.is_authenticated:
        return render(request, 'userprofile.html', {})
    query = UserSocialAuth.objects.filter(user = current_user.user_id)
    if not query:
        if current_user == request.user:
            return render(request, 'userprofile.html', {
                'user': current_user, 
                'needs_linking': True, 
                'message': current_user.username + " hasn't linked Spotify!"
            })
        return render(request, 'userprofile.html', {
            'user': current_user, 
            'message': current_user.username + " hasn't linked Spotify!"
        })
    social = query.first().extra_data
    refresh_token = social['refresh_token']
    access_token = social['access_token']
    auth_string = 'Bearer ' + access_token
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': auth_string,
    }
    current_track_data = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    if current_track_data.status_code == 204:
        return render(request, 'userprofile.html', {
            'user': current_user,
            'listening': False,
            'message': "Nothing right now!"
        })
    elif current_track_data.status_code == 503:
        return render(request, 'userprofile.html', {
            'user': current_user,
            'listening': False,
            'message': "Huh, not sure!"
        })
    elif current_track_data.status_code == 401:
        if current_user == request.user:
            return render(request, 'userprofile.html', {
            'user': current_user,
            'needs_linking': True,
            'message': request.user.username + " needs to re-authorize!"
            })
        return render(request, 'userprofile.html', {
            'user': current_user,
            'message': request.user.username + " needs to re-authorize!"
        })
    else:
        current_track_json = current_track_data.json()
        if 'item' in current_track_json:
            current_track_name = current_track_json['item']['name']
            current_track_artist = current_track_json['item']['artists'][0]['name']
            return render(request, 'userprofile.html', {
                'user': current_user,
                'listening': True,
                'current_track_name': current_track_name,
                'current_track_artist': current_track_artist
            })
    return render(request, 'userprofile.html', {'user': current_user, 'debug': current_track_data})

#-----------------------------------------------------------------------------------------#
class SignUpView(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

#-----------------------------------------------------------------------------------------#
