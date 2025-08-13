"""REST API views for the library."""
from rest_framework import viewsets
from .models import Track
from .serializers import TrackSerializer


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    http_method_names = ["get", "post", "head", "options"]
