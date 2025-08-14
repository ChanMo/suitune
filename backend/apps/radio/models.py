"""Data models for radio."""

from django.db import models


class Channel(models.Model):
    """A radio channel grouping tracks or streams."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.name


class RatingWeight(models.Model):
    """Weight applied to positive/negative feedback for a channel."""

    channel = models.OneToOneField(
        Channel, on_delete=models.CASCADE, related_name="rating_weight"
    )
    positive = models.FloatField(default=1.0)
    negative = models.FloatField(default=1.0)

    class Meta:
        ordering = ["id"]

    def apply(self, rating: int) -> float:
        """Return the weighted rating value."""
        return rating * (self.positive if rating > 0 else self.negative)

