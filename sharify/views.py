###########################################################################################
#   Imports
###########################################################################################
from sharify.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .models import Musicdata
from .forms import *
import random
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
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
    return render(request, 'userprofile.html', {})

#-----------------------------------------------------------------------------------------#
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

#-----------------------------------------------------------------------------------------#
