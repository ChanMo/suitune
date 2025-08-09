from rest_framework import serializers
from .models import Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = [
            'id', 'title', 'artist', 'album', 'duration',
            'channel', 'artwork_path', 'file_path'
        ]
