###########################################################################################
#   Imports
###########################################################################################
from django.urls import include, path

from . import views
from .views import UpdateUserView

#-----------------------------------------------------------------------------------------#
app_name = 'sharify'

urlpatterns = [
    path('search/artist/', views.get_artist, name='get_artist'),
    path('search/album/', views.get_album, name='get_album'),
    path('search/track/', views.get_track, name='get_track'),
    path('search/user/', views.get_user, name='get_user'),
    path('', views.homepage, name='homepage'),
    path('userprofile/', views.show_userprofile, name="userprofile"),
    path('todays_top_hits/', views.todays_top_hits, name='todays_top_hits'),
    path('comment/', views.comment, name='comment'),
    path('link_spotify/', views.link_spotify, name='link_spotify'),
    path('unlink_spotify/', views.unlink_spotify, name='unlink_spotify'),
    path('edit_profile/', views.UpdateUserView.as_view(), name='edit_profile'),
    path('add_friend/', views.add_friend, name='add_friend'),
    path('remove_friend/', views.remove_friend, name='remove_friend'),
    path('test_function', views.add_playlist_to_spotify, name='test_function'),
    path('track/', views.show_track, name='show_track'),
    path('create_playlist/', views.make_playlist_with_track, name='create_nonempty_playlist'),
    path('add_to_playlist/', views.add_to_playlist, name='create_nonempty_playlist'),
]

#-----------------------------------------------------------------------------------------#
