from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    # Test the publicly available ingredients API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required to acess the endpoint
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    # Test the private ingredients API
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.123',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        # Retrieving a list of ingredients
        Ingredient.objects.create(user=self.user, name='Laranja')
        Ingredient.objects.create(user=self.user, name='Sal')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        # Test that ingredients for the authenticated user are returned
        user2 = get_user_model().objects.create_user(
            'anotheruser',
            '12345'
        )
        Ingredient.objects.create(user=user2, name='Maçã')
        ingredient = Ingredient.objects.create(user=self.user, name='Romã')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successfull(self):
        # Test create a new ingredient
        payload = {'name': 'couve'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        # Test creating invalid ingredient fails
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        # Test filtering ingrediens by those assigned to recipes
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Frango'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Porco'
        )
        recipe = Recipe.objects.create(
            user=self.user,
            title='Frango de churrasco',
            time_minutes=80,
            price=6.00
        )

        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        # Test filtering ingredients by assigned return unique items
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Batata'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Alface'
        )
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Salada de camarão',
            time_minutes=20,
            price=15.00
        )
        recipe1.ingredients.add(ingredient)

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Javali no forno',
            time_minutes=90,
            price=25.00
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
