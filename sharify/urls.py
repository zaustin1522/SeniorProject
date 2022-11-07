###########################################################################################
#   Imports
###########################################################################################
from django.urls import path, include
from . import views

#-----------------------------------------------------------------------------------------#
app_name = 'sharify'

urlpatterns = [
    path('search/artist/', views.get_artist, name='get_artist'),
    path('search/album/', views.get_album, name='get_album'),
    path('search/track/', views.get_track, name='get_track'),
    path('', views.homepage, name='homepage'),
    path('userprofile/', views.show_userprofile, name="userprofile"),
    path('todays_top_hits/', views.todays_top_hits, name='todays_top_hits'),
    path('link_spotify', views.link_spotify, name='link_spotify'),
    path('test_oauth_endpoint', views.oauth_use_template, name='oauth_use_template')
]

#-----------------------------------------------------------------------------------------#
