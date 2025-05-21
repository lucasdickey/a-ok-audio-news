import uuid
from django.db import models
from django.utils import timezone

class DailyDigest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    title_en = models.CharField(max_length=255)
    title_zh = models.CharField(max_length=255, blank=True, null=True)
    description_en = models.TextField()
    description_zh = models.TextField(blank=True, null=True)
    keywords_en = models.CharField(max_length=255, blank=True, null=True)
    keywords_zh = models.CharField(max_length=255, blank=True, null=True)
    summary_text_en = models.TextField()
    summary_text_zh = models.TextField(blank=True, null=True)
    audio_url_en = models.URLField(blank=True, null=True)
    audio_url_zh = models.URLField(blank=True, null=True)
    llm_prompt = models.TextField()
    llm_response_raw = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Daily Digest'
        verbose_name_plural = 'Daily Digests'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.title_en}" 