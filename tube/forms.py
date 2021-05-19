from django import forms
from .models import Video,VideoComment

class VideoForm(forms.ModelForm):
    class Meta:
        model  = Video
        fields = ["title", "description", "movie", "category", "tag","thumbnail",]

class VideoEditForm(forms.ModelForm):
    class Meta:
        model  = Video
        fields = ["title", "description", "dt",]

class VideoCommentForm(forms.ModelForm):
    class Meta:
        model  = VideoComment
        fields = ["content", "target", ]
