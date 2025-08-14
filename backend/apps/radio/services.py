"""Service helpers for radio functionality."""
from .models import Channel


def apply_channel_rating(channel: Channel, rating: int) -> float:
    """Return rating weighted according to the channel configuration."""
    weight = getattr(channel, "rating_weight", None)
    if not weight:
        return float(rating)
    return weight.apply(rating)
