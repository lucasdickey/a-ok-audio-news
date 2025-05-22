from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyDigestViewSet, TTSView, PublishView, GenerateScriptView

router = DefaultRouter()
router.register(r'digests', DailyDigestViewSet, basename='dailydigest')

urlpatterns = [
    path('', include(router.urls)),
    path('tts/', TTSView.as_view(), name='tts'),
    path('publish/', PublishView.as_view(), name='publish'),
    path('generate-script/', GenerateScriptView.as_view(), name='generate-script'),
] 