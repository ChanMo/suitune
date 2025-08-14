"""Serializers for radio app."""
from rest_framework import serializers
from .models import Channel, RatingWeight


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["id", "name", "description"]


class RatingWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingWeight
        fields = ["id", "channel", "positive", "negative"]
