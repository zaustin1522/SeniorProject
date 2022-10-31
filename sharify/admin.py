from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Musicdata, User
from .forms import *

class Admin(UserAdmin):
    add_form = SignupForm
    form = PasswordChangeForm
    model = User
    list_display = ["username", "password",]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('some_extra_data',)}),
    )

# Register your models here.
admin.site.register(Musicdata)
admin.site.register(User, UserAdmin)
