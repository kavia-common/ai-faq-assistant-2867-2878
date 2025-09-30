from rest_framework.test import APITestCase
from django.urls import reverse
from .models import KnowledgeBaseEntry


class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})


class AskAndSearchTests(APITestCase):
    def setUp(self):
        KnowledgeBaseEntry.objects.create(
            title="Password Reset",
            question="How can I reset my password?",
            answer="Go to account settings and click 'Reset Password'.",
            tags=["account", "security"],
            is_active=True,
        )
        KnowledgeBaseEntry.objects.create(
            title="Two Factor",
            question="How to enable 2FA?",
            answer="Navigate to Security and enable Two-Factor Authentication.",
            tags=["security"],
            is_active=True,
        )

    def test_search(self):
        url = reverse('Search')
        response = self.client.get(url, {"query": "password"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data.get("results", [])) >= 1)

    def test_ask(self):
        url = reverse('Ask')
        response = self.client.post(url, {"question": "How do I reset my password?"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.data)
        self.assertIn("contexts", response.data)
