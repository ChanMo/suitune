from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.library.views import TrackViewSet
from . import views

router = DefaultRouter()
router.register("tracks", TrackViewSet, basename="track")

urlpatterns = [
    path("", include(router.urls)),
    path("me", views.me),
    path("next", views.next_track),
    path("feedback", views.feedback),
]
