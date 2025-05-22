from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DailyDigest
from .serializers import DailyDigestSerializer, TTSSerializer, PublishSerializer, ScriptGenerationSerializer
from datetime import date as dt_date

class DailyDigestViewSet(viewsets.ModelViewSet):
    queryset = DailyDigest.objects.all()
    serializer_class = DailyDigestSerializer

class TTSView(APIView):
    def post(self, request):
        serializer = TTSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Placeholder: Implement TTS logic here
        return Response({'audio_url': 'https://example.com/audio.mp3'}, status=status.HTTP_201_CREATED)

class PublishView(APIView):
    def post(self, request):
        serializer = PublishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Placeholder: Implement publish logic here
        return Response({'rss_url': 'https://example.com/rss.xml', 'status': 'published'}, status=status.HTTP_201_CREATED)

class GenerateScriptView(APIView):
    def post(self, request):
        serializer = ScriptGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_date = serializer.validated_data.get('date', dt_date.today())

        # Compose the LLM prompt for web-enabled news summary
        prompt = f"""
        Summarize the most relevant and interesting AI news for {target_date}.
        Use live web access to ensure the news is up-to-date and accurate.
        Return a concise, engaging script suitable for a podcast.
        """

        # Placeholder: Call your LLM provider here (e.g., OpenAI with web access)
        # For now, we'll mock the response
        llm_response = {
            'script': f"[Sample script for {target_date}]",
            'provider': 'openai',
            'web_access': True
        }

        # Save or update the DailyDigest entry
        digest, created = DailyDigest.objects.update_or_create(
            date=target_date,
            defaults={
                'summary_text_en': llm_response['script'],
                'llm_prompt': prompt,
                'llm_response_raw': llm_response,
            }
        )

        return Response({
            'date': str(target_date),
            'script': llm_response['script'],
            'digest_id': str(digest.id),
            'created': created
        }, status=status.HTTP_201_CREATED) 