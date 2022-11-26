#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Imports
###########################################################################################

#-----------------------------------------------------------------------------------------#


from django.http import Http404
from django.urls import reverse_lazy
from django.views import generic
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import random
import spotipy
from .profile import *
from .search import *
from .forms import *
from .models import Comment


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
def get_user(request: WSGIRequest):
    if request.method == 'GET':
        user = request.GET.get('user', None)
        if user is None:
            return render(request, "users.html", {})
        else:
            users = {}
            if user != "":
                print(user)
                users = find_user_by_name(user)
                print(users)
            return render(request, "user_results.html", users)

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
    return render(request, 'comment.html', {})

#-----------------------------------------------------------------------------------------#

class UpdateUserView(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('sharify:userprofile')

    def get_object(self):
        return self.request.user