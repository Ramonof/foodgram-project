from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from multiselectfield import MultiSelectField

User = get_user_model()

BREAFAST = 'breakfast'
LUNCH = 'lunch'
DINNER = 'dinner'

TAG_CHOICES = ((BREAFAST, 'Завтрак'),
               (LUNCH, 'Обед'),
               (DINNER, 'Ужин'))


class Recipe(models.Model):
    """Рецепты"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes",
        verbose_name="Автор")
    title = models.CharField(max_length=100, verbose_name="Название рецепта")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации")
    tags = MultiSelectField(choices=TAG_CHOICES, blank=True,
                            null=True, verbose_name="Теги")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")
    time = models.PositiveIntegerField(verbose_name="Время приготовления")
    image = models.ImageField(
        upload_to="recipes/",
        blank=True, null=True,
        verbose_name="Изображение")

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ингредиенты"""
    title = models.CharField(
        max_length=150, verbose_name="Название ингредиента")
    dimension = models.CharField(
        max_length=25, verbose_name="Единица измерения")

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.title} / {self.dimension}"


class RecipeIngredient(models.Model):
    """Описание ингредиентов и их колличества для рецепта"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент")
    amount = models.PositiveIntegerField(verbose_name="Количество")

    def add_ingredient(self, recipe_id, title, amount):
        ingredient = get_object_or_404(Ingredient, title=title)
        return self.objects.get_or_create(recipe_id=recipe_id,
                                          ingredient=ingredient, amount=amount)
