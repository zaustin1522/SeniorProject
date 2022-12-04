#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Imports
###########################################################################################

#-----------------------------------------------------------------------------------------#


from django.http import Http404
from django.urls import reverse_lazy
from django.views import generic
import json, exrex
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
                tracks = find_track_by_name(track)
            return render(request, "results/results.html", tracks)

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
def comment(request: WSGIRequest):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CommentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
             comment_on: Musicdata = Musicdata.objects.filter(track_id = form.cleaned_data['content_id']).first()
             user: MyUser = request.user
             comment: str = str(form.cleaned_data['comment'])
             Comment.objects.create(comment_on=comment_on, user=user, comment=comment)
    return render(request, 'social/comment.html', {})

#-----------------------------------------------------------------------------------------#
def playlist_search_by_name(request: WSGIRequest,):
    playlist_qset = Playlist.objects.all().filter(name__contains='name_from_form?')
    # not sure how you want to use this data to display on a page
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
def make_playlist(request: WSGIRequest):
    playlist = Playlist.objects.create(
            id = exrex.getone('[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}'),       # using regex to create id (duplication is possible here, but like django won't let me migrate the automated primary keys?)
            user = request.user,
            name = 'name_from_form?',
        )
    playlist.save()
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
def delete_playlist(request: WSGIRequest):
    playlist = Playlist.objects.all().filter(id='g90h-vne8-qgpd-bm2x')     # grab id from frontend
    playlist.delete()
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
def add_to_playlist(request: WSGIRequest):
    playlist = Playlist.objects.all().filter(id='l31s-q8jo-e4r9-lc8t')[0]     # playlist selected from frontend
    song = Musicdata.objects.all().filter(track_id='6f807x0ima9a1j3VPbc7VN')[0]    # song selected from frontend
    playlist.songs.append(song.pk)
    playlist.save()
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
def remove_from_playlist(request: WSGIRequest):
    playlist = Playlist.objects.all().filter(id='l31s-q8jo-e4r9-lc8t')[0]     # playlist selected from frontend
    song = Musicdata.objects.all().filter(track_id='6f807x0ima9a1j3VPbc7VN')[0]    # song selected from frontend
    playlist.songs.remove(song.pk)
    playlist.save()
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
def add_playlist_to_spotify(request: WSGIRequest):
    playlist = Playlist.objects.all().filter(id='l31s-q8jo-e4r9-lc8t')[0]     # playlist selected from frontend
    scope = [
        'playlist-modify-private',      # "Create, edit, and follow private playlists"
        'playlist-modify-public',       # "Create, edit, and follow playlists"
    ]
    auth_manager = SpotifyOAuth(scope=scope)
    token_info = auth_manager.refresh_access_token(refresh_token = request.user.profile.token_info['refresh_token'])
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp_playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist.name)
    sp.playlist_add_items(playlist_id = sp_playlist['id'], items=playlist.songs)
    return render(request, 'base/home.html', {})

#-----------------------------------------------------------------------------------------#
class UpdateUserView(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'profiles/edit_profile.html'
    success_url = reverse_lazy('sharify:userprofile')

    def get_object(self):
        return self.request.user