###########################################################################################
#   Imports
###########################################################################################
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm, UserCreationForm)

User = get_user_model()

#-----------------------------------------------------------------------------------------#
class SearchForm(forms.Form):
    artist = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    from_year = forms.IntegerField(required=False)
    to_year = forms.IntegerField(required=False)

#-----------------------------------------------------------------------------------------#
class CommentForm(forms.Form):
    content_id = forms.HiddenInput()
    user = forms.HiddenInput()
    comment = forms.CharField(widget=forms.TextInput(), required=True)

#-----------------------------------------------------------------------------------------#
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )

#-----------------------------------------------------------------------------------------#
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

#-----------------------------------------------------------------------------------------#
class PasswordChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'password')

#-----------------------------------------------------------------------------------------#

class EditUserProfileForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Enter your first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Enter your last name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder' : 'Enter your email'}))
    bio = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Enter your bio'}))
    friends_are_public = forms.BooleanField(required=False, label="Public Friend List")
    playlists_are_public = forms.BooleanField(required=False, label="Public playlists")
    likes_are_public = forms.BooleanField(required=False, label="Public likes")
    password = None
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'friends_are_public', 'playlists_are_public', 'likes_are_public']
