"""Data models for audio library."""
from django.db import models


class Track(models.Model):
    """A single playable audio track."""

    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True)
    audio_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.title} - {self.artist}".strip(" -")
