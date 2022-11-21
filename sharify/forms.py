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
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio']
