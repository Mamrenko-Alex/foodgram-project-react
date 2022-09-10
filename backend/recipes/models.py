from django.db import models
from django.utils.html import format_html
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    hexcolor = models.CharField(max_length=7, default='#ffffff')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
    
    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.hexcolor
        )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name = 'Название ингридиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name', ]
        constraints = [
            models.UniqueConstraint(fields=[
                'name', 'measurement_unit'],
                name='unique_ingredient')
        ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        default='Some string',
        blank=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите, как можно подробнее, этапы приготовления',
        blank=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recieps',
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингридиенты',
        related_name='recipes',
        blank=True
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Добавьте изображиние',
        upload_to='recipes/images/',
        blank=True
    )
    cooking_time = models.IntegerField(
        default=1,
        verbose_name='Время приготовления',
        blank=True,
        validators=[
            MinValueValidator(
                1,
                'Минимальное время приготовления 1 минута'
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date', ]
    
    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='recipe',
    )
    amount = models.IntegerField(
        default=1,
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1,
                ('Минимальное количество для каждого '
                'ингридиента 1, независимо от единицы измерения')
            )
        ]
    )

    class Meta:
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ['-id', ]
        constraints = [
            models.UniqueConstraint(fields=[
                'recipe', 'ingredients'],
                name='unique_ingredient_in_recipe')
        ]

    def __str__(self) -> str:
        return (f'{self.ingredients.name} - '
                f'{self.amount}{self.ingredients.measurement_unit}')



class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['-id', ]
        constraints = [
            models.UniqueConstraint(fields=[
                'user', 'recipe'],
                name='unique_recipe_for_user')
        ]

    def __str__(self) -> str:
        return f'Ваши избранные рецепты {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_list'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_list'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ['-id', ]
        constraints = [
            models.UniqueConstraint(fields=[
                'user', 'recipe'], 
                name='unique_shoping_list_user')
        ]
    
    def __str__(self) -> str:
        return (f'{self.recipe.name}')
