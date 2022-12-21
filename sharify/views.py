#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Imports
###########################################################################################

#-----------------------------------------------------------------------------------------#


from django.http import Http404
from django.urls import reverse_lazy
from django.views import generic
import json
from random import randint
from .profiles import *
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
                albums = find_album_by_name(album, request.user)
            return render(request, "results/album_results.html", {'results': albums})

#-----------------------------------------------------------------------------------------#
def get_track(request: WSGIRequest):
    if request.method == 'GET':
        track = request.GET.get('track', None)
        if track is None:
            return render(request, "search/track.html", {})
        else:
            tracks = {}
            user: MyUser = request.user
            if track != "":
                tracks = find_track_by_name(track, user)
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
        return show_profile_for(request, request.user)
    findUser: MyUser = MyUser.objects.filter(username__iexact = username).first()
    if findUser is None:
        return show_profile_for(request, request.user)
    return show_profile_for(request, findUser)

#-----------------------------------------------------------------------------------------#
def show_track(request: WSGIRequest):
    track_id = request.GET.get('id', None)
    if track_id is None:
        return get_track(request)
    try:
        track: Musicdata = Musicdata.objects.get(track_id = track_id)
    except Musicdata.DoesNotExist:
        return get_track(request)
    return render(request, 'items/view_track.html', {
        'track': track
    })

#-----------------------------------------------------------------------------------------#
def comment(request: WSGIRequest):
    on_type: str = request.GET.get('type')
    if on_type == "album":
        try:
            comment_on: Musicdata = Musicdata.objects.filter(album_id = request.GET.get('id')).get(album_liason = True)
        except Musicdata.DoesNotExist:
            return HttpResponse(status=400)
    else:
        comment_on: Musicdata = Musicdata.objects.get(track_id = request.GET.get('id'))
    user: MyUser = MyUser.objects.get(id=request.user.id)
    comment: str = request.GET.get('comment')
    Comment.objects.create(comment_on=comment_on, on_type= on_type, user=user, comment=comment)
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
    Playlist.objects.create(
            user = user,
            name = name
        )
    return HttpResponse(status=201)

#-----------------------------------------------------------------------------------------#
def make_playlist_with_track(request: WSGIRequest):
    name = request.GET.get("playlist_name")
    track_id = request.GET.get("track_id")
    print(request.body)
    try:
        track = Musicdata.objects.get(track_id = track_id)
    except Musicdata.DoesNotExist:
        return HttpResponse(status=400)
    
    user: MyUser = request.user
    playlist = Playlist.objects.create(
            user = user,
            name = name
        )
    playlist.songs.add(track)
    return HttpResponse(status=201, content="Successfully made playlist \"" + name + "\" containing the song " + str(track) + "\nPlease refresh the page or make another search to add songs to the playlist.")

#-----------------------------------------------------------------------------------------#
def delete_playlist(request: WSGIRequest):
    target = request.GET.get("deleting_id")
    return delete_playlist_by_id(target)

#-----------------------------------------------------------------------------------------#
def delete_playlist_by_id(target: str):
    try:
        playlist = Playlist.objects.get(id=target)     # grab id from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    playlist.delete()
    return HttpResponse(status=205)

#-----------------------------------------------------------------------------------------#
def add_to_playlist(request: WSGIRequest):
    new_song = request.GET.get("track_id")
    target = request.GET.get("playlist_id")
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    try:
        song = Musicdata.objects.get(track_id=new_song)    # song selected from frontend
    except Musicdata.DoesNotExist:
        return HttpResponse(status=422, content="No such track with id " + new_song)

    playlist_songs = list(playlist.songs.values('track_id'))
    playlist_songs = list(playlist_songs[0].values())
    if song in playlist_songs:
        return HttpResponse(status=406, content=str(song) + " is already in playlist \"" + playlist.name + "\"")
    playlist.songs.add(song.track_id)
    playlist.save()
    return HttpResponse(status=200, content="Successfully added " + str(song) + " to playlist \"" + playlist.name + "\"")

#-----------------------------------------------------------------------------------------#
def remove_from_playlist(request: WSGIRequest):
    to_delete = request.GET.get("track_id")
    target = request.GET.get("playlist_id")
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    try:
        song: Musicdata = playlist.songs.get(track_id=to_delete)    # song selected from frontend
    except Musicdata.DoesNotExist:
        return HttpResponse(status=422, content="No such track with id " + to_delete)

    playlist.songs.remove(song)
    playlist.save()
    if playlist.songs.count() == 0:
        delete_playlist_by_id(target)
    return HttpResponse(status=200)

#-----------------------------------------------------------------------------------------#
def rename_playlist(request: WSGIRequest):
    new_name = request.GET.get("new_name")
    target = request.GET.get("playlist_id")
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)

    playlist.name = new_name
    playlist.save()
    return HttpResponse(status=202)

#-----------------------------------------------------------------------------------------#
def add_playlist_to_spotify(request: WSGIRequest):
    user: MyUser = request.user
    target = request.GET.get("playlist_id")
    method = request.GET.get("method")
    global auth_manager
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)
    
    songs: list = list(playlist.songs.values_list("track_id", flat=True))
    sp = spotipy.Spotify(auth=get_access_token(user))
    spotify_playlists: json = sp.user_playlists(user=user.profile.spotify_id)
    sp_p_ids: dict = {}
    sp_p_items: dict = {}
    for item in spotify_playlists['items']:
        sp_p_items[item['id']] = sp.playlist_items(playlist_id=item['id'])['items']
        scrape_playlist(sp_p_items[item['id']])
        sp_p_ids[item['name']] = item['id']

    # playlist either has no spotify id OR that playlist is no longer in the spotify account
    if playlist.spotify_id is None or playlist.spotify_id not in sp_p_ids.values():
        # playlist with the same name already exists in spotify account
        if playlist.name in sp_p_ids.keys():
            if method == "safe":
                return HttpResponse("safe rename", status=200)
            elif method == "merge":
                sp_tracks = sp_p_items[sp_p_ids[playlist.name]]
                sp_track_ids: list = []
                for track in sp_tracks:
                    sp_track_ids.append(track['track']['id'])
                sh_track_ids: list = []
                for track in playlist.songs.all():
                    track: Musicdata
                    sh_track_ids.append(track.track_id)
                missing_from_sp: list = []
                missing_from_sh: list = []
                for track in sh_track_ids:
                    if track not in sp_track_ids:
                        missing_from_sp.append(track)
                for track in sp_track_ids:
                    if track not in sh_track_ids:
                        missing_from_sh.append(track)
                missing_from_sh = Musicdata.objects.filter(track_id__in=missing_from_sh)
                for track in missing_from_sh:
                    playlist.songs.add(track)
                playlist.spotify_id = sp_p_ids[playlist.name]
                playlist.save()
                sp.user_playlist_add_tracks(user.profile.spotify_id, playlist.spotify_id, missing_from_sp)
                return HttpResponse("merge success", status=202)
            elif method == "clobber":
                sp.user_playlist_replace_tracks(user.profile.spotify_id, sp_p_ids[playlist.name], list(playlist.songs.all().values_list('track_id', flat=True)))
                sp.user_playlist_change_details(user.profile.spotify_id, playlist.spotify_id, playlist.name)
                return HttpResponse("clobber success", status=202)
        #playlist by that name does not exist on spotify account, create new
        else:
            sp_playlist = sp.user_playlist_create(user=user.profile.spotify_id, name=playlist.name)
            playlist.spotify_id=sp_playlist['id']
            playlist.save()
            sp.playlist_add_items(playlist_id=playlist.spotify_id, items=songs)
            return HttpResponse("playlist created", status=201)
    # playlist exists on spotify already
    else:
        if method == "safe":
            sp.user_playlist_change_details(user.profile.spotify_id, playlist.spotify_id, playlist.name)
            return HttpResponse("safe exists", status=200)
        elif method == "merge":
            sp_tracks = sp_p_items[playlist.spotify_id]
            sp_track_ids: list = []
            for track in sp_tracks:
                sp_track_ids.append(track['track']['id'])
            sh_track_ids: list = []
            for track in playlist.songs.all():
                track: Musicdata
                sh_track_ids.append(track.track_id)
            missing_from_sp: list = []
            missing_from_sh: list = []
            for track in sh_track_ids:
                if track not in sp_track_ids:
                    missing_from_sp.append(track)
            for track in sp_track_ids:
                if track not in sh_track_ids:
                    missing_from_sh.append(track)
            missing_from_sh = Musicdata.objects.filter(track_id__in=missing_from_sh)
            for track in missing_from_sh:
                playlist.songs.add(track)
            playlist.save()
            if len(missing_from_sp) > 0:
                sp.user_playlist_add_tracks(user.profile.spotify_id, playlist.spotify_id, missing_from_sp)
            return HttpResponse("merge success", status=202)
        elif method == "clobber":
            sp.user_playlist_replace_tracks(user.profile.spotify_id, playlist.spotify_id, list(playlist.songs.all().values_list('track_id', flat=True)))
            sp.user_playlist_change_details(user.profile.spotify_id, playlist.spotify_id, playlist.name)
            return HttpResponse("clobber success", status=202)

#-----------------------------------------------------------------------------------------#
def refresh_playlist(request: WSGIRequest):
    user: MyUser = request.user
    target = request.GET.get("playlist_id")
    global auth_manager
    try:
        playlist = Playlist.objects.get(id=target)     # playlist selected from frontend
    except Playlist.DoesNotExist:
        return HttpResponse(status=422, content="No such playlist with id " + target)
    sp = spotipy.Spotify(auth=get_access_token(user))
    spotify_playlist = sp.user_playlist(user.profile.spotify_id, playlist.spotify_id)
    playlist.name = spotify_playlist['name']
    playlist.save()
    items_json = spotify_playlist['tracks']['items']
    scrape_playlist(items_json)
    for music in playlist.songs.all():
        playlist.songs.remove(music)
    for track in items_json:
        playlist.songs.add(Musicdata.objects.get(track_id=track['track']['id']))
    return HttpResponse("refreshed", status=200)

#-----------------------------------------------------------------------------------------#
def get_playlists(request: WSGIRequest):
    user: MyUser = request.user
    global auth_manager
    sp = spotipy.Spotify(auth=get_access_token(user))
    spotify_playlists: json = sp.user_playlists(user=user.profile.spotify_id)
    users_playlists: list = []
    users_playlists_data: list = []
    for spotify_playlist in spotify_playlists['items']:
        if spotify_playlist['owner']['id'] == user.profile.spotify_id:
            playlist_items = sp.playlist_items(spotify_playlist['id'])['items']
            scrape_playlist(playlist_items)
            users_playlists.append(playlist_items)
            users_playlists_data.append(spotify_playlist)
    
    for i in range(len(users_playlists)):
        data = users_playlists_data[i]
        try:
            existing = Playlist.objects.get(spotify_id=data['id'])
            existing.delete()
        except Playlist.DoesNotExist:
            None
        new_playlist: Playlist = Playlist.objects.create(name=data['name'], spotify_id=data['id'], user=user)
        for item in users_playlists[i]:
            new_playlist.songs.add(Musicdata.objects.get(track_id=item['track']['id']))
        new_playlist.save()


    return HttpResponse("refreshed", status=200)

#-----------------------------------------------------------------------------------------#
def manage_playlist(request: WSGIRequest):
    if not request.user.is_authenticated:
        return render(request, 'base/home.html')

    user: MyUser = request.user
    playlist_id = request.GET.get("playlist_id")
    if playlist_id is None:
        return render(request, 'base/home.html')

    try:
        playlist = Playlist.objects.get(id = playlist_id)
    except Playlist.DoesNotExist:
        return render(request, 'base/home.html')
    
    playlist_user = playlist.user
    if user.username != playlist_user.username:
        return render(request, 'base/home.html')
    
    return render(request, 'items/view_playlist.html', {"playlist": playlist})

#-----------------------------------------------------------------------------------------#
class UpdateUserView(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'profiles/edit_profile.html'
    success_url = reverse_lazy('sharify:userprofile')

    def get_object(self):
        return self.request.user

#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views for Recommendations
###########################################################################################

#-----------------------------------------------------------------------------------------#
def like_song(request: WSGIRequest):
    user: MyUser = request.user
    target_id = request.GET.get('track_id')
    try:
        song = Musicdata.objects.get(track_id=target_id)    # song selected from frontend
    except Musicdata.DoesNotExist:
        return HttpResponse("Track doesn't exist.", status=400)
    if song not in user.liked_songs.all():
        user.liked_songs.add(song)
        user.save()
    return HttpResponse("liked-" + target_id, status=200)

#-----------------------------------------------------------------------------------------#
def unlike_song(request: WSGIRequest):  # option to unlike song to remove it from recommendation seeding
    user: MyUser = request.user
    target_id = request.GET.get('track_id')
    try:
        song = Musicdata.objects.get(track_id=target_id)    # song selected from frontend
    except Musicdata.DoesNotExist:
        return HttpResponse("Track doesn't exist.", status=400)
    if song in user.liked_songs.all():
        user.liked_songs.remove(song)
        user.save()
    return HttpResponse("unliked-" + target_id, status=200)

#-----------------------------------------------------------------------------------------#
def get_artist_ids(track: Musicdata, user: MyUser):
    sp = spotipy.Spotify(auth=get_access_token(user))
    fresh_data = sp.album_tracks(track.album_id)
    for fresh_track in fresh_data['items']:
        artist_ids: list = []
        for artist in fresh_track['artists']:
            artist_ids.append(artist['id'])
        try:
            existing_track = Musicdata.objects.get(track_id=fresh_track['id'])
            existing_track.artist_ids = artist_ids
            existing_track.save()
        except Musicdata.DoesNotExist:
            continue
    refreshed_track = Musicdata.objects.get(track_id = track.track_id)
    return refreshed_track.artist_ids

#-----------------------------------------------------------------------------------------#
def recommend_songs(request: WSGIRequest):
    if not request.user.is_authenticated:
        return render(request, 'registration/login.html')
    user: MyUser = request.user
    track_seeds: list = []
    artists: list = []
    for track in user.liked_songs.all():
        track: Musicdata
        track_seeds.append(track.track_id)
        if len(track.artist_ids) == 0:
            artists.extend(get_artist_ids(track, user))
        else:
            artists.extend(track.artist_ids)
    
    artist_seed_dict = {artist_id: artists.count(artist_id) for artist_id in artists}
    sorted_artist_seeds = dict(sorted(artist_seed_dict.items(), key=lambda item: item[1], reverse=True))
    artist_seeds = list(sorted_artist_seeds.keys())[:1]
    
    if len(track_seeds) == 0:
        return show_userprofile(request)
    track_seeds=track_seeds[:10]
    random.shuffle(track_seeds)
    track_seeds=track_seeds[:4]


    spotipy_controller = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    recommended_songs = []
    for track in spotipy_controller.recommendations(seed_artists=artist_seeds, seed_tracks=track_seeds)['tracks']:
        scrape_album(track['album']['id'])
        try:
            song = Musicdata.objects.get(track_id = track['id'])
        except Musicdata.DoesNotExist:
            continue
        recommended_songs.append((song, list(Comment.objects.filter(on_type = 'track').filter(comment_on_id = song.track_id).order_by('-posted_at'))))


    # Return the id of up to 20 songs
    results = [recommended_songs[i:i+2] for i in range(0, len(recommended_songs), 2)]
    context = {
        'tracks': results
    }
    return render(request, 'search/recommendations.html', context)
