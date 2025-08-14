"""Serializers for playback app."""
from rest_framework import serializers
from .models import Playback, Feedback


class PlaybackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playback
        fields = ["id", "track", "user", "started_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "playback", "rating", "comment", "created_at"]
