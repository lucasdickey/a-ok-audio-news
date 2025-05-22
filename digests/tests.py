from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from digests.models import DailyDigest
import uuid
from datetime import date

class DailyDigestAPITestCase(APITestCase):
    def setUp(self):
        self.list_url = reverse('dailydigest-list')
        self.today = date.today()
        self.data = {
            'date': self.today,
            'title_en': 'Test Title',
            'title_zh': '测试标题',
            'description_en': 'Test description',
            'description_zh': '测试描述',
            'keywords_en': 'test,api',
            'keywords_zh': '测试,接口',
            'summary_text_en': 'Test script',
            'summary_text_zh': '测试脚本',
            'audio_url_en': 'https://example.com/audio_en.mp3',
            'audio_url_zh': 'https://example.com/audio_zh.mp3',
            'llm_prompt': 'Prompt',
            'llm_response_raw': {},
        }

    def test_crud_lifecycle(self):
        # Create
        response = self.client.post(self.list_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        digest_id = response.data['id']

        # Retrieve
        detail_url = reverse('dailydigest-detail', args=[digest_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title_en'], self.data['title_en'])

        # Update
        update_data = {'title_en': 'Updated Title'}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title_en'], 'Updated Title')

        # Delete
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm deletion
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 