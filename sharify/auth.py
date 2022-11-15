#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Views for Authorization
###########################################################################################

#-----------------------------------------------------------------------------------------#


import json

import requests
import spotipy
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from sharify.log import logmessage
from sharify.models import SpotifyProfile
from sharify.models import User as MyUser


#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Loading Environment and Setting Spotify Controller
###########################################################################################

#-----------------------------------------------------------------------------------------#
load_dotenv()
global_current_user: MyUser

# Instantiating the Spotipy unauthenticated controller
spotipy_controller = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
# Scope for Token (Privileges), listed in order of appearance
scope = [                   # "You agree that Sharify will be able to:"
                                # "View your Spotify account data"
    #'user-read-email',              # "Your email"
    #'user-read-private',            # "The type of Spotify subscription you have, your account country and your settings for explicit content filtering"
                                    # "Your name and username, your profile picture, how many followers you have on Spotify and your public playlists"
                                # "View your activity on Spotify"
    #'user-read-recently-played',    # "Content you have recently played"
    'user-read-currently-playing',  # "The content you are playing"
    #'user-read-playback-state',     # "The content you are playing and Spotify Connect devices information"
    #'user-library-read',            # "What you’ve saved in Your Library"
    'user-top-read',                # "Your top artists and content"
    #'user-follow-read',             # "Who you follow on Spotify"
    #'playlist-read-private',        # "Playlists you’ve made and playlists you follow"
    #'playlist-read-collaborative',  # "Your collaborative playlists"
    #'user-read-playback-position',  # "Your position in content you have played"
                                # "Take actions in Spotify on your behalf"
    #'user-modify-playback-state',   # "Control Spotify on your devices"
    #'ugc-image-upload',             # "Upload images to personalize your profile or playlist cover"
    #'user-library-modify',          # "Add and remove items in Your Library"
    #'playlist-modify-private',      # "Create, edit, and follow private playlists"
    #'playlist-modify-public',       # "Create, edit, and follow playlists"
    #'user-follow-modify',           # "Manage who you follow on Spotify"
    #'streaming',                    # "Stream and control Spotify on your other devices"
    ]

# Sets scope for SpotifyOAuth oject so it knows what privileges we're requesting for login.
auth_manager = SpotifyOAuth(scope=scope)


#-----------------------------------------------------------------------------------------#
def link_spotify(request: WSGIRequest):
    if request.GET.get('code'):
        user: MyUser = request.user
        profile: SpotifyProfile | None = user.profile
        token_info: json = auth_manager.get_access_token(request.GET.get('code'), check_cache=False)
        # if user hasn't linked before
        if profile is None:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + str(token_info['access_token'])
            }
            response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            user_profile: json = json.loads(response.content)
            display_name = user_profile['display_name']
            spotify_id = user_profile['id']
            follower_total = user_profile['followers']['total']
            api_access = user_profile['href']
            if len(user_profile['images']) != 0:
                avatar_url = user_profile['images'][0]['url']
            else:
                avatar_url = "https://i.scdn.co/image/ab6775700000ee8555c25988a6ac314394d3fbf5"
            user.profile = SpotifyProfile.objects.create(
                display_name = display_name, 
                spotify_id = spotify_id, 
                follower_total = follower_total, 
                api_access = api_access, 
                avatar_url = avatar_url, 
                token_info = token_info
            )
            user.save()
            logmessage(type="LINKED", msg=user.username+" connected Spotify ID "+spotify_id)
        return redirect('/userprofile/')        # Redirect to User Profile.

    # If that all failed, get authorization from Spotify
    auth_manager.show_dialog = True
    return HttpResponseRedirect(auth_manager.get_authorize_url())

#-----------------------------------------------------------------------------------------#
def unlink_spotify(request: WSGIRequest):
    if request.user.is_authenticated:
        current_user: MyUser = request.user
        if current_user.profile is not None:
            current_user: MyUser = request.user
            profile = current_user.profile
            spotify_id = profile.spotify_id
            current_user.profile = None
            profile.delete()
            current_user.save()
            logmessage(type="UNLINKED", msg=current_user.username+" disconnected Spotify ID "+spotify_id)
        return redirect('/userprofile/')
    return redirect('/')
