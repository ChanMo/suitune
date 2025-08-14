from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from apps.library.serializers import TrackSerializer
from apps.radio import radio_service


@api_view(["GET"])
def me(request):
    """Return basic information about the current user."""
    user = request.user
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return Response({"username": None})
    return Response({"username": user.get_username()})


@api_view(["GET"])
def next_track(request):
    """Return the next recommended track for a channel."""
    channel = request.query_params.get("channel", "default")
    track, stream_url = radio_service.next_track(channel)
    if not track:
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = TrackSerializer(track).data
    return Response({"track": data, "stream_url": stream_url})


@api_view(["POST"])
def feedback(request):
    """Record feedback for a track and acknowledge it."""
    channel = request.data.get("channel", "default")
    track_id = request.data.get("track_id")
    liked = request.data.get("liked")
    if track_id is None or liked is None:
        return Response({"error": "track_id and liked are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        radio_service.submit_feedback(channel, int(track_id), bool(liked))
        return Response({"status": "received"}, status=status.HTTP_201_CREATED)
    except (ValueError, TypeError):
        return Response({"error": "Invalid track_id or liked format"}, status=status.HTTP_400_BAD_REQUEST)
