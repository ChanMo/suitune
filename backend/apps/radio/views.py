"""REST API views for radio."""
from rest_framework import viewsets
from .models import Channel, RatingWeight
from .serializers import ChannelSerializer, RatingWeightSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class RatingWeightViewSet(viewsets.ModelViewSet):
    queryset = RatingWeight.objects.all()
    serializer_class = RatingWeightSerializer
