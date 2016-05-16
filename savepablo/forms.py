from django import forms
from models import *
from django.contrib.auth.models import User
from django.forms import ModelForm

class RegistrationForm(forms.Form):
  user_name = forms.CharField(max_length=20)
  first_name = forms.CharField(max_length=20)
  last_name = forms.CharField(max_length=20)
  password1 = forms.CharField(max_length=200,
                             label='Password',
                              widget = forms.PasswordInput())
  password2 = forms.CharField(max_length=200,
                             label='Confirm Password',
                              widget = forms.PasswordInput())
  email = forms.EmailField()

  def clean(self):
    cleaned_data = super(RegistrationForm,self).clean()

    password1 = cleaned_data.get('password1')
    password2 = cleaned_data.get('password2')

    if password1 and password2 and password1 != password2:
      raise forms.ValidationError('Passwords did not match')

    return cleaned_data


  def clean_user_name(self):
    username = self.cleaned_data.get('user_name')
    
    if User.objects.filter(username__exact=username):
      raise forms.ValidationError('User name already taken')

    return username

class SearchForm(forms.Form):
  username = forms.CharField(max_length=30)
  def clean(self):
    cleaned_data=super(SearchForm, self).clean()
    return cleaned_data
