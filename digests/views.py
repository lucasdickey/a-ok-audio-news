from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DailyDigest
from .serializers import (
    DailyDigestSerializer,
    TTSSerializer,
    PublishSerializer,
    ScriptGenerationSerializer,
)
from datetime import date as dt_date
import os
import anthropic
import base64
import requests
from .utils.vercel_blob import upload_bytes, BlobUploadError

# Configure OpenAI once at import time
# Import our multi-agent pipeline
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents_pipeline import generate_episode

# Configure Anthropic once at import time
anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

class DailyDigestViewSet(viewsets.ModelViewSet):
    queryset = DailyDigest.objects.all()
    serializer_class = DailyDigestSerializer

class TTSView(APIView):
    def post(self, request):
        serializer = TTSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data["text"]
        lang = serializer.validated_data.get("lang", "en")
        voice = serializer.validated_data.get("voice", "9DDKJLIKJqVKLbRZb3kO")  # default ElevenLabs voice

        eleven_api_key = os.getenv("ELEVEN_API_KEY")
        if not eleven_api_key:
            return Response(
                {"error": "ELEVEN_API_KEY not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Map simple voice name to ElevenLabs voice_id if needed.
        # For now we assume `voice` is a voice_id.
        voice_id = voice

        tts_endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": eleven_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.71,
                "similarity_boost": 0.5,
            },
        }

        try:
            resp = requests.post(tts_endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            audio_bytes = resp.content
        except Exception as exc:
            return Response(
                {"error": f"TTS generation failed: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Upload to Vercel Blob
        try:
            audio_url = upload_bytes(audio_bytes)
        except BlobUploadError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Update DailyDigest row if date provided
        digest_id = None
        target_date_str = request.data.get("date")
        if target_date_str:
            try:
                from datetime import date as _d
                target_date = _d.fromisoformat(target_date_str)
                digest, _ = DailyDigest.objects.update_or_create(
                    date=target_date,
                    defaults={"audio_url_en": audio_url},
                )
                digest_id = str(digest.id)
            except Exception:
                pass

        return Response({
            "audio_url": audio_url,
            "voice_id": voice_id,
            "lang": lang,
            "digest_id": digest_id,
        }, status=status.HTTP_201_CREATED)

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

        # Using the agents_pipeline for script generation
        prompt = f"Generated APE INTELLIGENCE DAILY script for {target_date} using multi-agent pipeline with web search capabilities."

        # Use the existing Anthropic-based agents pipeline
        try:
            episode_result = generate_episode(
                date_str=str(target_date),
                with_editor=True,
                human_review=False
            )
            
            script_text = episode_result.get('script', '')
            llm_response = {
                "research": episode_result.get('research', ''),
                "summary": episode_result.get('summary', ''),
                "script": script_text,
                "generated_via": "agents_pipeline"
            }
        except Exception as exc:
            # Fallback: still return a stub so pipeline doesn't crash
            script_text = f"[LLM call failed: {exc}]"
            llm_response = {"error": str(exc)}

        # Save or update the DailyDigest entry
        digest, created = DailyDigest.objects.update_or_create(
            date=target_date,
            defaults={
                'summary_text_en': script_text,
                'llm_prompt': prompt,
                'llm_response_raw': llm_response,
            }
        )

        return Response({
            'date': str(target_date),
            'script': script_text,
            'digest_id': str(digest.id),
            'created': created
        }, status=status.HTTP_201_CREATED) 
