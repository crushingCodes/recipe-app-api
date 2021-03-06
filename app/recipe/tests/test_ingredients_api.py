from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
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

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Broccoli'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Bread'
        )
        recipe = Recipe.objects.create(
            user=self.user,
            title='Pasta',
            time_minutes=5,
            price=3
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(
            INGREDIENT_URL,
            {
                'assigned_only': 1
            }
        )
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Eggs benedict',
            time_minutes=5,
            price=6.44
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Coriander eggs on toast',
            time_minutes=4,
            price=2.34
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(
            INGREDIENT_URL,
            {
                'assigned_only': 1
            }
        )
        self.assertEqual(len(res.data), 1)
