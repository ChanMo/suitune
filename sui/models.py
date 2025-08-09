from django.db import models


class Track(models.Model):
    CHANNEL_CHOICES = [
        ('music', 'Music'),
        ('talk', 'Talk'),
        ('tv', 'TV'),
        ('ambient', 'Ambient'),
    ]

    file_path = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True)
    album = models.CharField(max_length=255, blank=True)
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    file_size = models.PositiveIntegerField(default=0, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    artwork_path = models.CharField(max_length=255, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    play_count = models.PositiveIntegerField(default=0)
    last_played_at = models.DateTimeField(null=True, blank=True)
    liked = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)

    class Meta:
        db_table = 'sui_track'


class Playback(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    skipped = models.BooleanField(default=False)
    source_channel = models.CharField(max_length=16, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'sui_playback'
