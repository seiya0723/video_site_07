from rest_framework import serializers

from .models import Video,VideoComment

class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Video
        fields =["title","description","tag","category","movie","image"]

class VideoCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoComment
        fields = ["content","target"]