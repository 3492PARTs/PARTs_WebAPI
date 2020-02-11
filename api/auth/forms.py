from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(), required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(), required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(required=True)
