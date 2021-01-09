from django import forms
from .models import video

class VideoForm(forms.ModelForm):
    class Meta:
        model= video
        fields= [ "videofile","title","description"]

class userForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    email = forms.CharField()
    gender = forms.CharField()
    birthdate = forms.DateField()





