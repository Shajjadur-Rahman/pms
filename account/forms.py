from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile



class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # self.fields['user_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input email'})
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input password again'})


    class Meta:
        model  = User
        fields = ['email', 'username', 'password1', 'password2']



class ProfileForm(forms.ModelForm):
    class Meta:
        model  = Profile
        fields = ['phone_no', 'portfolio_link', 'profile_image', 'gender', 'invited_by']