from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.error_messages = {
            'password_mismatch':("As duas senhas são diferentes."),
        }
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
