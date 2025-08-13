from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.library.models import Track
from apps.library.serializers import TrackSerializer


@api_view(["GET"])
def me(request):
    """Return basic information about the current user."""
    user = request.user
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return Response({"username": None})
    return Response({"username": user.get_username()})


@api_view(["GET"])
def next_track(request):
    """Return the next track to play (first track for demo)."""
    track = Track.objects.order_by("id").first()
    if not track:
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = TrackSerializer(track).data
    return Response({"track": data, "stream_url": track.audio_url})


@api_view(["POST"])
def feedback(request):
    """Accept simple feedback payload and acknowledge it."""
    return Response({"status": "received"}, status=status.HTTP_201_CREATED)
