import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def recipe_image_upload_url(recipe_id):
    """Return url for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def recipe_detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


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


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeTests(TestCase):
    """Test unauthenticate recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            'other@email.com',
            'password123'
        )
        sample_recipe(user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_detail(self):
        """Test retrieving the details of the recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a valid recipe is successful"""
        payload = {
            'title': 'Chocolate cheescake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Salad')
        payload = {
            'title': 'Avocado Salad',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Prawns')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with Patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Chicken Tikka',
            'tags': [new_tag.id]
        }
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(payload['title'], recipe.title)
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with Put"""
        recipe = sample_recipe(user=self.user)
        payload = {
            'title': 'Tortilla',
            'time_minutes': 10,
            'price': 3.00
        }
        url = recipe_detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(payload['title'], recipe.title)
        self.assertEqual(payload['price'], recipe.price)
        self.assertEqual(payload['time_minutes'], recipe.time_minutes)
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        # Help keep the file system clear from clogging up
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an email to recipe"""
        url = recipe_image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # Seek sets the pointer back to the start of the file
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')
            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        url = recipe_image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
