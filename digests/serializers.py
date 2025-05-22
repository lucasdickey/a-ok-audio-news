from rest_framework import serializers
from .models import DailyDigest

class DailyDigestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyDigest
        fields = '__all__'

class TTSSerializer(serializers.Serializer):
    text = serializers.CharField()
    lang = serializers.CharField(default='en')
    voice = serializers.CharField(default='default')

class PublishSerializer(serializers.Serializer):
    audio_url = serializers.URLField()
    title = serializers.CharField()
    description = serializers.CharField()
    date = serializers.DateField()
    lang = serializers.CharField(default='en')
    keywords = serializers.CharField()
    transcript_url = serializers.URLField(required=False)

class ScriptGenerationSerializer(serializers.Serializer):
    date = serializers.DateField(required=False) 