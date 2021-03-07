from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from core.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


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


class TestPublicIngredientAPI(TestCase):
    """Test the publicly available ingredient api"""

    def setUp(self):
        self.client = APIClient()

    def test_that_login_required(self):
        """Test that login is required to use the endpoint"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class TestPrivateIngredientAPI(TestCase):
    """Test the private ingredients api"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)
