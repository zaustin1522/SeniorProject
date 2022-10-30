from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Musicdata, User

# Register your models here.
admin.site.register(Musicdata)
admin.site.register(User, UserAdmin)
