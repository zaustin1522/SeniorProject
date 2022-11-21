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
    path('', views.homepage, name='homepage'),
    path('userprofile/', views.show_userprofile, name="userprofile"),
    path('todays_top_hits/', views.todays_top_hits, name='todays_top_hits'),
    path('comment/', views.comment, name='comment'),
    path('link_spotify/', views.link_spotify, name='link_spotify'),
    path('unlink_spotify/', views.unlink_spotify, name='unlink_spotify'),
    path('edit_profile/', views.UpdateUserView.as_view(), name='edit_profile'),
    ,
]

#-----------------------------------------------------------------------------------------#
