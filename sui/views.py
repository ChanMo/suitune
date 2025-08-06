from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Track
from .serializers import TrackSerializer


def home(request):
    return render(request, "sui/index.html")


class NextTrackView(APIView):
    def get(self, request):
        track = Track.objects.order_by('?').first()
        if not track:
            return Response({'detail': 'no tracks available'}, status=status.HTTP_404_NOT_FOUND)
        data = TrackSerializer(track).data
        data['stream_url'] = f"/sui_stream/{track.path}"
        return Response(data)


class FeedbackView(APIView):
    def post(self, request):
        return Response({'status': 'ok'})
