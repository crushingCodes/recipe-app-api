from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

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

    def test_retrieving_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Broccoli')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients only returned for authorized user"""
        user2 = sample_user(email='other@email.com', name='other')
        Ingredient.objects.create(user=user2, name='chocolate')
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='strawberry'
        )

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.filter(user=self.user)
        ingredient_exists = Ingredient.objects.filter(
            name=ingredient.name,
            user=ingredient.user
        ).exists()
        self.assertTrue(ingredient_exists)
        self.assertEqual(len(ingredients), 1)

    def test_create_ingredient_successful(self):
        """Test creating valid ingredient is successful"""
        payload = {'name': 'Cucumber', 'user': self.user}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredient_exists = Ingredient.objects.filter(
            name=payload['name']
        ).exists()
        self.assertTrue(ingredient_exists)

    def test_create_ingredient_invalid(self):
        """Test create invalid ingredient fails"""
        payload = {'name': '', 'user': self.user}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
