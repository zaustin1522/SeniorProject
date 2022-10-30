###########################################################################################
#   Imports
###########################################################################################
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
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
