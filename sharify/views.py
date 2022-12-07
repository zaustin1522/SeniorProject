#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Imports
###########################################################################################

#-----------------------------------------------------------------------------------------#


from django.http import Http404
from django.urls import reverse_lazy
from django.views import generic
import json
from .profile import *
from .search import *
from .forms import *
from .models import Comment, Playlist


#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Basic Views
###########################################################################################

#-----------------------------------------------------------------------------------------#
def homepage(request):
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
class SignUpView(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views for Search and Browse
###########################################################################################

#-----------------------------------------------------------------------------------------#
def todays_top_hits(request: WSGIRequest):
    tracks = []
    # Grabs the playlist items object and grabs dict key 'items' to get an array of tracks
    items: json = spotipy_controller.playlist_items(playlist_id='37i9dQZF1DXcBWIGoYBM5M')['items']
    for item in items:
        item: json
        tracks.append(item['track']['id'])
    
    scrape_playlist(items)
    random.shuffle(tracks)
    context = {
        # Splits first 10 tracks
        'tracks': tracks[:10]
    }
    return render(request, 'search/todays_top_hits.html', context)

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
            return render(request, 'search/artist.html', {
                'form': form,
                'results': albumGrid,
                'type': "album"
            })
        else:
            raise Http404('Something went wrong')
    else:
        form = SearchForm()
        return render(request, 'search/artist.html', {'form': form})

#-----------------------------------------------------------------------------------------#
def get_album(request: WSGIRequest):
    if request.method == 'GET':
        album = request.GET.get('album', None)
        if album is None:
            return render(request, "search/album.html", {})
        else:
            albums = {}
            if album != "":
                albums = find_album_by_name(album)
            return render(request, "results/results.html", albums)

#-----------------------------------------------------------------------------------------#
def get_track(request: WSGIRequest):
    if request.method == 'GET':
        track = request.GET.get('track', None)
        if track is None:
            return render(request, "search/track.html", {})
        else:
            tracks = {}
            if track != "":
                tracks = find_track_by_name(track, request.user)
            if not request.user.is_authenticated:
                return render(request, "results/track_results.html", {"results": tracks})
            else:
                playlists = Playlist.objects.filter(user_id=request.user.id)
                return render(request, "results/track_results.html", {"results": tracks, "playlists": playlists})


#-----------------------------------------------------------------------------------------#
def get_user(request: WSGIRequest):
    if request.method == 'GET':
        user = request.GET.get('user-search', None)
        if user is None:
            return render(request, "search/users.html", {})
        else:
            user_data = {}
            if user != "":
                user_data = find_user_by_name(user)
            return render(request, "results/user_results.html", user_data)

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views for Profile Browsing
###########################################################################################

#-----------------------------------------------------------------------------------------#
def show_userprofile(request: WSGIRequest):
    username = request.GET.get('username', None)
    if username is None:
        logmessage(type = "PROFILE", msg = "No username specified: assuming " + str(request.user))
        return show_profile_for(request, request.user)
    findUser: MyUser = MyUser.objects.filter(username__iexact = username).first()
    if findUser is None:
        logmessage(type = "PROFILE", msg = "No user found matching " + username + ": assuming " + str(request.user))
        return show_profile_for(request, request.user)
    logmessage(type = "PROFILE", msg = "User " + username + " found: Displaying profile...")
    return show_profile_for(request, findUser)

#-----------------------------------------------------------------------------------------#
def show_track(request: WSGIRequest):
    track_id = request.GET.get('id', None)
    if track_id is None:
        logmessage(type = "TRACK", msg = "No id specified: redirecting to track browse.")
        return get_track(request)
    try:
        track: Musicdata = Musicdata.objects.get(track_id = track_id)
    except Musicdata.DoesNotExist:
        logmessage(type = "TRACK", msg = "Invalid id specified: redirecting to track browse.")
        return get_track(request)
    logmessage(type = "TRACK", msg = "Track " + str(track) + " found: Displaying...")
    return render(request, 'items/view_track.html', {
        'track': track
    })

#-----------------------------------------------------------------------------------------#
def comment(request: WSGIRequest):
    comment_on: Musicdata = Musicdata.objects.get(track_id = request.GET.get('track_id'))
    user: MyUser = MyUser.objects.get(id=request.user.id)
    comment: str = request.GET.get('comment')
    Comment.objects.create(comment_on=comment_on, user=user, comment=comment)
    return HttpResponse(status=201)

#-----------------------------------------------------------------------------------------#
def playlist_search_by_name(request: WSGIRequest,):
    query = request.GET.get("query")
    playlist_qset = Playlist.objects.filter(name__icontains=query)
    temp = list(playlist_qset)
    resp = []
    [resp.append(playlist) for playlist in temp if playlist not in resp]
    # Randomize to get different results each time
    random.shuffle(resp)
    # Return the id of up to 9 playlists
    playlists = [item['album_id'] for item in resp[:9]]
    playlistGrid = [playlists[i:i+3] for i in range(0, len(playlists), 3)]
    return {
        'results': playlistGrid,
	    'type': "playlist"
    }

#-----------------------------------------------------------------------------------------#
def make_playlist(request: WSGIRequest):
    name = request.GET.get("playlist_name")
    user: MyUser = request.user
    playlist = Playlist.objects.create(
            user = user,
            name = name
        )
    playlist.save()
    return HttpResponse(status=201)

#-----------------------------------------------------------------------------------------#
def delete_playlist(request: WSGIRequest):
    target = request.GET.get("deleting_id")
    try:
        playlist = Playlist.objects.get(id=target)     # grab id from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    playlist.delete()
    return HttpResponse(status=200)

#-----------------------------------------------------------------------------------------#
def add_to_playlist(request: WSGIRequest):
    new_song = request.GET.get("song_id")
    target = request.GET.get("playlist_id")
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    try:
        song = Musicdata.objects.get(track_id=new_song)    # song selected from frontend
    except Musicdata.DoesNotExist:
        return HttpResponse(status=422, content="No such track with id " + new_song)

    playlist.songs.add(song.track_id)
    playlist.save()
    return HttpResponse(status=201)

#-----------------------------------------------------------------------------------------#
def remove_from_playlist(request: WSGIRequest):
    new_song = request.GET.get("song_id")
    target = request.GET.get("playlist_id")
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    try:
        song = playlist.songs.get(track_id=new_song)    # song selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such track with id " + new_song)

    playlist.songs.remove(song.track_id)
    playlist.save()
    return HttpResponse(status=201)

#-----------------------------------------------------------------------------------------#
def add_playlist_to_spotify(request: WSGIRequest):
    user: MyUser = request.user
    target = request.GET.get("playlist_id")
    global auth_manager
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    songs: list = []
    for song in playlist.songs:
        songs.append(song.track_id)
    sp = spotipy.Spotify(auth=get_access_token(user))
    logmessage(msg=playlist.songs.values_list("track_id"))
    sp_playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist.name)
    sp.playlist_add_items(playlist_id = sp_playlist['id'], items=songs)
    return HttpResponse(status=200)

#-----------------------------------------------------------------------------------------#
class UpdateUserView(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'profiles/edit_profile.html'
    success_url = reverse_lazy('sharify:userprofile')

    def get_object(self):
        return self.request.user