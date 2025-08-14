"""Data models for playback."""

from django.conf import settings
from django.db import models
from apps.library.models import Track


class Playback(models.Model):
    """Represents a single playback of a track."""

    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="playbacks")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.track} @ {self.started_at:%Y-%m-%d %H:%M:%S}"


class Feedback(models.Model):
    """Stores user feedback for a particular playback."""

    playback = models.ForeignKey(
        Playback, on_delete=models.CASCADE, related_name="feedback"
    )
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Feedback {self.rating} for playback {self.playback_id}"

