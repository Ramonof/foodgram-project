import operator
from functools import reduce

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RecipeForm
from .models import TAG_CHOICES, Recipe, RecipeIngredient

User = get_user_model()


def index(request):
    tags, tags_filter = tag_collect(request)
    if tags_filter:
        recipes = Recipe.objects.filter(tags_filter)
    else:
        recipes = Recipe.objects.all()
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags
    }
    return render(request, 'index.html', context)


def user_page(request, username):
    author = get_object_or_404(User, username=username)
    tags, tags_filter = tag_collect(request)
    if tags_filter:
        recipes = Recipe.objects.filter(tags_filter).filter(
            author_id=author.id)
    else:
        recipes = Recipe.objects.filter(author_id=author.id)
    paginator = Paginator(recipes, 9)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
        'author': author
    }
    return render(request, 'user_page.html', context)


def recipe_page(request, username, recipe_id):
    author = get_object_or_404(User, username=username)
    recipe = get_object_or_404(Recipe, id=recipe_id, author_id=author.id)
    ingredients = RecipeIngredient.objects.filter(recipe_id=recipe_id)
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'author': author
    }
    return render(request, 'recipe_page.html', context)


@login_required
def feed(request):
    user = request.user
    authors = User.objects.filter(
        following__subscriber=user).prefetch_related("recipes")
    paginator = Paginator(authors, 3)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        'authors': authors,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'feed.html', context)


@login_required
def new_recipe(request):
    form_title = 'Создание рецепта'
    btn_caption = "Создать рецепт"
    form = RecipeForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        ingredients_names = request.POST.getlist('nameIngredient')
        ingredients_values = request.POST.getlist('valueIngredient')
        if len(ingredients_names) == len(ingredients_values):
            count = len(ingredients_names)
        else:
            return redirect("new")
        new_recipe = form.save(commit=False)
        new_recipe.author = request.user
        new_recipe.save()
        ingridients_names_values = zip(ingredients_names, ingredients_values)
        for ingridient in list(ingridients_names_values):
            RecipeIngredient.add_ingredient(
                RecipeIngredient,
                new_recipe.id,
                ingridient[0],
                ingridient[1]
            )
        return redirect("index")

    context = {
        'form_title': form_title,
        'btn_caption': btn_caption,
        'form': form
    }
    return render(request, 'form_recipe.html', context)


@login_required
def edit_recipe(request, username, recipe_id):
    form_title = 'Редактирование рецепта'
    btn_caption = "Сохранить"
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = get_object_or_404(User, username=username)
    recipe_redirect = redirect(
        "recipe", username=user.username, recipe_id=recipe_id)
    is_breakfast = 'breakfast' in recipe.tags
    is_lunch = 'lunch' in recipe.tags
    is_dinner = 'dinner' in recipe.tags
    ingredients = RecipeIngredient.objects.filter(
        recipe_id=recipe_id)

    if request.user != user:
        return recipe_redirect
    form = RecipeForm(request.POST or None,
                      files=request.FILES or None, instance=recipe)

    if form.is_valid():
        ingredients_names = request.POST.getlist('nameIngredient')
        ingredients_values = request.POST.getlist('valueIngredient')
        if len(ingredients_names) == len(ingredients_values):
            count = len(ingredients_names)
        else:
            return redirect("edit_recipe",
                            username=username, recipe_id=recipe_id)
        form.save()
        RecipeIngredient.objects.filter(recipe_id=recipe.id).delete()
        ingredients_names_values = zip(ingredients_names, ingredients_values)
        for ingredient in list(ingredients_names_values):
            RecipeIngredient.add_ingredient(
                RecipeIngredient,
                recipe.id,
                ingredient[0],
                ingredient[1]
            )
        return recipe_redirect

    context = {
        'form_title': form_title,
        'btn_caption': btn_caption,
        'form': form,
        'recipe': recipe,
        'is_breakfast': is_breakfast,
        'is_lunch': is_lunch,
        'is_dinner': is_dinner,
        'ingredients': ingredients
    }
    return render(request, 'form_recipe.html', context)


@login_required
def favorites(request):
    user = request.user
    tags, tags_filter = tag_collect(request)
    if tags_filter:
        recipes = Recipe.objects.filter(tags_filter).filter(
            favorite_recipe__user=user)
    else:
        recipes = Recipe.objects.filter(
            favorite_recipe__user=user)
    paginator = Paginator(recipes, 12)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags
    }
    return render(request, 'favorites.html', context)


@login_required
def wishlist(request):
    user = request.user
    recipes = Recipe.objects.filter(
        wishlist_recipe__user=user)
    context = {
        'recipes': recipes
    }
    return render(request, 'wishlist.html', context)


def tag_collect(request):
    """Собирает теги для фильтрации рецептов на странице"""
    tags = []
    for label, _ in TAG_CHOICES:
        if request.GET.get(label, ""):
            tags.append(label)
    if tags:
        tags_filter = reduce(
            operator.or_, (Q(tags__contains=tag)for tag in tags))
        return tags, tags_filter
    else:
        return tags, None
