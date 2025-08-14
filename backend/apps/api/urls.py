from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.library.views import TrackViewSet
from apps.playback.views import PlaybackViewSet, FeedbackViewSet
from apps.radio.views import ChannelViewSet, RatingWeightViewSet
from . import views

router = DefaultRouter()
router.register("tracks", TrackViewSet, basename="track")
router.register("playbacks", PlaybackViewSet, basename="playback")
router.register("feedback", FeedbackViewSet, basename="feedback")
router.register("channels", ChannelViewSet, basename="channel")
router.register("rating-weights", RatingWeightViewSet, basename="ratingweight")

urlpatterns = [
    path("", include(router.urls)),
    path("me", views.me),
    path("next", views.next_track),
    path("feedback", views.feedback),
]
