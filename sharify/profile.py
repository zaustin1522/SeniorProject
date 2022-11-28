#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Utility Method for Profile Rendering
###########################################################################################

#-----------------------------------------------------------------------------------------#


from django.http import HttpResponse
from django.shortcuts import render

from sharify.auth import *
from sharify.scrape import *


#-----------------------------------------------------------------------------------------#
def get_friend_objects(current_user: MyUser):
    friend_ids: list = current_user.friends
    friend_query: MyUser.objects.filter(id__in=friend_ids)
    friend_list: list = list(friend_query)
    return friend_list

#-----------------------------------------------------------------------------------------#
def add_friend(request: WSGIRequest):
    other: int = request.GET.get('other')
    current_user: MyUser = request.user
    new_friend = MyUser.objects.get(id = other)

    my_friends: list = current_user.friends
    my_pending: json = current_user.pending
    your_friends: list = new_friend.friends
    your_pending: json = new_friend.pending
    my_inbox: list = my_pending['in']
    my_outbox: list = my_pending['out']
    your_inbox: list = your_pending['in']
    your_outbox: list = your_pending['out']
    
    # if already friends
    if new_friend.id in my_friends:
        return HttpResponse(status=304)
    # if current_user has already sent a friend request to new_friend
    if new_friend.id in my_outbox:
        return HttpResponse(status=304)
    
    # if current_user is replying to new_friend's request
    if new_friend.id in my_inbox:
        my_friends.append(new_friend.id)
        your_friends.append(current_user.id)
        my_inbox.remove(new_friend.id)
        your_outbox.remove(current_user.id)
        current_user.friends = my_friends
        new_friend.friends = your_friends
        current_user.pending['in'] = my_inbox
        new_friend.pending['out'] = your_outbox
        current_user.save()
        new_friend.save()
        return HttpResponse(status=202)
    
    # if current_user is making a request to new_friend
    if new_friend.id not in my_outbox:
        my_outbox.append(new_friend.id)
        your_inbox.append(current_user.id)
        current_user.pending['out'] = my_outbox
        new_friend.pending['in'] = your_inbox
        current_user.save()
        new_friend.save()
        return HttpResponse(status=201)

#-----------------------------------------------------------------------------------------#
def remove_friend(request: WSGIRequest):
    other: int = request.GET.get('other')
    current_user: MyUser = request.user
    removing = MyUser.objects.get(id = other)
    my_friends: list = current_user.friends
    my_pending: json = current_user.pending
    your_friends: list = removing.friends
    your_pending: json = removing.pending
    my_inbox: list = my_pending['in']
    my_outbox: list = my_pending['out']
    your_inbox: list = your_pending['in']
    your_outbox: list = your_pending['out']

    # removing friend from friend list
    if removing.id in my_friends:
        my_friends.remove(removing.id)
        your_friends.remove(current_user.id)
        my_inbox.append(removing.id)
        your_outbox.append(current_user.id)
        current_user.friends = my_friends
        removing.friends = your_friends
        current_user.pending['in'] = my_inbox
        removing.pending['out'] = your_outbox
        current_user.save()
        removing.save()
        return HttpResponse(status=200)
    
    # revoking friend request
    if removing.id in my_outbox:
        my_outbox.remove(removing.id)
        your_inbox.remove(current_user.id)
        current_user.pending['out'] = my_outbox
        removing.pending['in'] = your_inbox
        current_user.save()
        removing.save()
        return HttpResponse(status=200)

#-----------------------------------------------------------------------------------------#
def show_profile_for(request: WSGIRequest, current_user: MyUser):
    global global_current_user

    # No user is logged in, no user was requested; go to homepage
    if current_user.username == '':
        return redirect('/')

    global_current_user = current_user

    # User does not have a linked Spotify Profile
    if current_user.profile is None:
        return render(request, 'profiles/userprofile.html', {
            'current_user': current_user,
            'can_link': current_user == request.user,
            'needs_linking': True,
            'message': current_user.username + " hasn't linked Spotify!",
            'fav_artist': "What IS art, really?"
        }) 

    # Check if User's access token is expired, and refresh it if needed.
    get_access_token(current_user)
    profile: SpotifyProfile | None = current_user.profile
    
    # Get the User's most-played artist from Spotify.
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(profile.token_info['access_token'])
    }
    params = {
        'time_range': 'medium_term',
        'limit': '1',
        'offset': '0',
    }
    response = requests.get('https://api.spotify.com/v1/me/top/artists', params=params, headers=headers)
    if response.status_code == 403:
        return render(request, 'profiles/userprofile.html', {
            'current_user': current_user,
            'needs_linking': current_user == request.user,
            'message': "Something went wrong, try again later!",
            'fav_artist': "What IS art, really?"
        }) 

    fav_artist_data: json = json.loads(response.content)
    if fav_artist_data is not None and 'items' in fav_artist_data and len(fav_artist_data['items']) != 0:
        fav_artist: str = fav_artist_data['items'][0]['name']
    else:
        fav_artist: str = current_user.username + " doesn't play favorites."

    # Get the User's most-played song from Spotify.
    response = requests.get('https://api.spotify.com/v1/me/top/tracks', params=params, headers=headers)
    if response.status_code == 403:
        return render(request, 'profiles/userprofile.html', {
            'current_user': current_user,
            'needs_linking': current_user == request.user,
            'message': "Something went wrong, try again later!",
            'fav_artist': fav_artist
        }) 
    fav_track_data: json = json.loads(response.content)
    if fav_track_data is not None and 'items' in fav_track_data:
        #their favorite track wasn't in the DB: check whole album, add if necessary (2 API calls inside)
        if Musicdata.objects.filter(track_id=fav_track_data['items'][0]['id']).count() == 0:
            scrape_album(fav_track_data['items'][0]['album']['id'])
        fav_track = Musicdata.objects.get(track_id = fav_track_data['items'][0]['id'])
    else:
        # haha, high level humor
        fav_track: str = "4'33\" by John Cage"


    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    if response.status_code == 200:
        current_track_data: json = json.loads(response.content)
    elif response.status_code == 204:
        current_track_data = None
    elif response.status_code == 403:
        return render(request, 'profiles/userprofile.html', {
            'current_user': current_user,
            'needs_linking': current_user == request.user,
            'message': "Something went wrong, try again later!",
            'fav_artist': fav_artist,
            'fav_track': fav_track
        }) 


    # User is linked to Spotify AND is currently listening to something.
    if current_track_data is not None:
        if 'item' in current_track_data:
            if 'currently_playing_type' in current_track_data:
                if not current_track_data['currently_playing_type'] == 'ad':
                    track = current_track_data['item']

                    # Track isn't in DB: check whole album, add if necessary (2 API calls inside)
                    if Musicdata.objects.filter(track_id=track['id']).count() == 0:
                        scrape_album(track['album']['id'])

                    current_track: Musicdata = Musicdata.objects.get(track_id=track['id'])
                    return render(request, 'profiles/userprofile.html', {
                        'current_user': current_user,
                        'listening': True,
                        'current_track': str(current_track),
                        'fav_artist': fav_artist,
                        'fav_track': fav_track
                    })
                else:
                    return render(request, 'profiles/userprofile.html', {
                        'current_user': current_user,
                        'listening': False,
                        'message': "An ad!",
                        'fav_artist': fav_artist,
                        'fav_track': fav_track
                    })
    # User is linked to Spotify, but isn't listening to anything.
    return render(request, 'profiles/userprofile.html', {
        'current_user': current_user,
        'listening': False,
        'message': "Nothing right now!",
        'fav_artist': fav_artist,
        'fav_track': fav_track
    })
