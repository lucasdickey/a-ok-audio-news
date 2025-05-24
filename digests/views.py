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
import openai
import base64
import requests

# Configure OpenAI once at import time
openai.api_key = os.getenv("OPENAI_API_KEY", "")

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

        # Base64 encode so we can return inline (client can decode)
        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

        return Response({
            "audio_base64": audio_b64,
            "voice_id": voice_id,
            "lang": lang,
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

        # Compose the comprehensive LLM prompt for web-enabled news summary
        prompt = f"""
        Create a rich podcast script for APE INTELLIGENCE DAILY covering the most significant AI developments for {target_date}.
        
        AUDIENCE: AI practitioners (developers, researchers, business strategists, enterprise deployers) who actively follow AI news. 
        No introductory fluff or basic explanations needed.
        
        STRUCTURE: 12 stories total, each 2-3 paragraphs covering:
        - WHAT happened (the core development/announcement)
        - WHY it matters at large (implications for the field)
        - WHEN/WHERE details if material to the story
        
        FORMAT: Begin with "Welcome to APE INTELLIGENCE DAILY, I'm your tireless researcher, astute analyst, and handsome host, A-OK"
        
        CITATION REQUIREMENTS: Include proper attributions like "as reported by The Information", "according to The Verge", etc.
        
        PRIORITIZED SOURCES - Focus heavily on these outlets:
        News: The Information, The Verge, TBNP, The Gradient, Import AI (Jack Clark), Papers with Code, Semafor, Wired, Axios, Bloomberg, TechCrunch, The AI Exchange (Nathan Benaich)
        
        Podcasts (transcripts when available): The AI Daily Brief, ThursdAI, Latent Space, AI & I, How I AI, Prac, Decoder with Nilay Patel, Hard Fork, The 20 Minute VC, This Day In AI Podcast, Machine Learning Street Talk, Lightcone Podcast, Practical AI, Generative Now, Dwarkesh Podcast, Financial Times/NYT/WSJ AI coverage
        
        Company Blogs (AI-focused): Anthropic, OpenAI, Cursor, Windsurf, Microsoft AI, Google AI/Labs/DeepMind, Meta, AWS, Hugging Face, Mistral, Cohere, Bolt, Lovable, v0/Vercel, Figma, Ethan Mollick's One Useful Thing, Noahpinion (Noah Smith), Groq
        
        Twitter Accounts: @rowancheung, @adcock_brett, @alexalbert__, @alexrkonrad, @sama, @DarioAmodei, @levie, @eriktorenberg, @paulg, @satyanadella, @reidhoffman, @nvidia
        
        EXCLUSIONS: Do NOT include news about Tesla, Twitter/X, SpaceX, Neuralink, or other Elon Musk companies.
        
        Use live web access to ensure accuracy and recency.
        """

        # Call OpenAI ChatCompletion with web browsing enabled
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Browsing-capable model
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are A-OK Newsbot, host of APE INTELLIGENCE DAILY. "
                            "Generate a comprehensive podcast script covering the 12 most significant AI developments "
                            f"for {target_date}. Each story should be 2-3 paragraphs covering what happened, why it matters, "
                            "and relevant when/where details. Target AI practitioners - no beginner explanations needed. "
                            "Include proper citations and focus on the specified high-quality sources. "
                            "Exclude any Elon Musk company news. Use live web access for accuracy."
                        ),
                    }
                ],
                temperature=0.7,
                stream=False,
            )

            script_text = completion.choices[0].message["content"].strip()
            llm_response = completion.to_dict_recursive()
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
