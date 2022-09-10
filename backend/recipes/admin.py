from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientAmount,
    FavoriteRecipe,
    ShoppingList
)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'hexcolor')


class IngredintAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'text',
        'pub_date',
        'author',
        'image',
        'cooking_time'
    )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags', 'cooking_time')
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    list_filter = ('recipe',)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('users',)


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('users',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredintAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
