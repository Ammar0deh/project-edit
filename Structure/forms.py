from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': 'input'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': 'input'
    }))


class SignupForm(UserCreationForm):
    class Meta :
        model = User
        fields = ('email' ,'username','password1','password2')
        
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'username',
        'class': 'input'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'email address',
        'class': 'input'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'password',
        'class': 'input'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat password',
        'class': 'input'
    }))