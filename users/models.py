from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from recipes.models import Recipe

User = get_user_model()


class Follow(models.Model):
    """Подписки пользователь-пользователь"""
    UniqueConstraint(
        name='unique',
        fields=['order'],
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriber")
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        constraints = [ 
            UniqueConstraint(name='unique', fields=['subscriber', 'following'],) 
        ]


class Favorite(models.Model):
    """Избранные рецепты"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite_subscriber")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorite_recipe")


class Wishlist(models.Model):
    """Список покупок"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_subscriber")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="wishlist_recipe")
