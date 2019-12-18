from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
  email = forms.EmailField(max_length=254, required=False, help_text='(Optional)')

  def __init__(self, *args, **kwargs):
    super(UserCreationForm, self).__init__(*args, **kwargs)

    self.fields['password1'].help_text = '''Minimum 8 characters. Can't contain username, contain all numbers, or be a commonly used password.'''

  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')