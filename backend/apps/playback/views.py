"""REST API views for playback."""

from rest_framework import viewsets
from .models import Playback, Feedback
from .serializers import PlaybackSerializer, FeedbackSerializer


class PlaybackViewSet(viewsets.ModelViewSet):
    queryset = Playback.objects.all()
    serializer_class = PlaybackSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

