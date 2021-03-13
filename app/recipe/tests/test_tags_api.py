from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


def sample_user(email='test@email.com', name='test', password='Password1'):
    """Create sample user"""
    try:
        return get_user_model().objects.get(email=email)
    except Exception:
        return get_user_model().objects.create_user(
            email=email,
            name=name,
            password=password
        )


class PublicTagsAPITest(TestCase):
    """Test public endpoints for tags"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITagsTest(TestCase):
    """Test private endpoints for tags"""
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")
        res = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned belong to the authenticated user"""
        other_user = sample_user(email='other@email.com', name='Other')
        # Should be ignored
        Tag.objects.create(user=other_user, name="Fruity")
        # Only this should be returned
        tag = Tag.objects.create(user=self.user, name="Comfort food")

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a tag works"""
        payload = {
            'name': "Entree",
            'user': sample_user()
        }
        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tag_exists = Tag.objects.filter(name=payload['name']).exists()
        self.assertTrue(tag_exists)

    def test_create_tag_invalid(self):
        """Test creating a tag with invalid name fails"""
        payload = {
            'name': '',
            'user': sample_user()
        }
        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        tag_exists = Tag.objects.filter(name='')
        self.assertFalse(tag_exists)
