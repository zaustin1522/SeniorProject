from django.urls import path
from . import views

app_name = 'sharify'

urlpatterns = [
    path('search/artist/', views.get_artist, name='get_artist'),
    path('search/album/', views.get_album, name='get_album'),
    path('search/track/', views.get_track, name='get_track'),
    path('', views.homepage, name='homepage'),
    path('login/', views.show_login, name='login'),
    path('userprofile/', views.show_userprofile, name="userprofile"),
    path('todays_top_hits', views.todays_top_hits, name='todays_top_hits')
]

