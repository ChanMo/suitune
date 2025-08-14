from __future__ import annotations

import random
from collections import defaultdict, deque
from typing import Deque, Dict, Optional, Tuple, TYPE_CHECKING

from django.apps import apps

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from apps.library.models import Track


class RadioService:
    """Score tracks based on feedback and sample next track."""

    def __init__(self, cooldown_size: int = 2, rng: Optional[random.Random] = None) -> None:
        self.cooldown_size = cooldown_size
        self.rng = rng or random.Random()
        self.scores: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.cooldowns: Dict[str, Deque[int]] = defaultdict(lambda: deque(maxlen=self.cooldown_size))

    def submit_feedback(self, channel: str, track_id: int, liked: bool) -> None:
        """Adjust score for a track on a channel based on feedback."""
        delta = 1 if liked else -1
        new_score = self.scores[channel][track_id] + delta
        if new_score < 0:
            new_score = 0
        self.scores[channel][track_id] = new_score

    def _candidates(self, channel: str):
        TrackModel = apps.get_model("library", "Track")
        cooldown_ids = list(self.cooldowns[channel])
        return TrackModel.objects.exclude(id__in=cooldown_ids)

    def next_track(self, channel: str) -> Tuple[Optional["Track"], Optional[str]]:
        """Return a recommended track and signed URL."""
        candidates = self._candidates(channel)
        if not candidates:
            return None, None
        weights = [self.scores[channel][t.id] + 1 for t in candidates]
        choice = self.rng.choices(candidates, weights=weights, k=1)[0]
        self.cooldowns[channel].append(choice.id)
        url = self.sign_url(choice.audio_url)
        return choice, url

    @staticmethod
    def sign_url(url: str) -> str:
        """Return a signed URL (placeholder)."""
        return url
