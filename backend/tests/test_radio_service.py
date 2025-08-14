from typing import List

from django.test import TestCase

from apps.library.models import Track
from apps.radio.services import RadioService


class DummyRandom:
    """Deterministic choice helper selecting the highest weight."""

    def choices(self, population: List, weights: List[float], k: int = 1):  # type: ignore[override]
        index = max(range(len(population)), key=lambda i: weights[i])
        return [population[index]]


class RadioServiceTest(TestCase):
    def setUp(self):
        self.tracks = [
            Track.objects.create(title=f"T{i}", artist="A", audio_url=f"u{i}")
            for i in range(3)
        ]

    def test_cooldown_prevents_replay(self):
        service = RadioService(cooldown_size=2, rng=DummyRandom())
        channel = "test"
        first, _ = service.next_track(channel)
        second, _ = service.next_track(channel)
        third, _ = service.next_track(channel)
        ids = [t.id for t in [first, second, third]]
        self.assertEqual(ids, [self.tracks[0].id, self.tracks[1].id, self.tracks[2].id])

    def test_feedback_affects_weights_and_channels(self):
        service = RadioService(cooldown_size=0, rng=DummyRandom())
        channel_a = "a"
        channel_b = "b"
        # Positive feedback for track2 on channel A, negative for track1
        service.submit_feedback(channel_a, self.tracks[1].id, True)
        service.submit_feedback(channel_a, self.tracks[0].id, False)
        chosen_a, _ = service.next_track(channel_a)
        chosen_b, _ = service.next_track(channel_b)
        self.assertEqual(chosen_a.id, self.tracks[1].id)
        self.assertEqual(chosen_b.id, self.tracks[0].id)
