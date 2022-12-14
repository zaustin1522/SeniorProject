from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Musicdata, Playlist, User, SpotifyProfile
from .forms import *

class Admin(UserAdmin):
    add_form = SignupForm
    form = PasswordChangeForm
    model = User
    list_display = ["username", "password",]

# Register your models here.
admin.site.register(Musicdata)
admin.site.register(User, UserAdmin)
admin.site.register(Playlist)
admin.site.register(SpotifyProfile)
