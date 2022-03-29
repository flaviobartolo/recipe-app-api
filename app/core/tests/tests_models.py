from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@test.com', password='testpass'):
    # create a sample user
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # Test creating a new user with an email is successful
        email = 'test@xpto.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test the email for a new user is normalized
        email = 'test@TEST.com'
        user = get_user_model().objects.create_user(email, '12345test')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Test create user with no email raises error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')

    def test_create_new_superuser(self):
        # Creating a new super user
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )

        self.assertTrue(user.is_superuser, user.is_staff)

    def test_tag_str(self):
        # Test the tag string representation
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # Test the ingredient string representation
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # Test the recipe string representation
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Caldo Verde',
            time_minutes=5,
            price=10.00
        )

        self.assertEqual(str(recipe), recipe.title)
