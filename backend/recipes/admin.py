from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, 
                    IngredientAmount, Recipe, 
                    ShoppingList, Tag)


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'hexcolor')


class IngredintAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    list_filter = ('recipe', 'ingredients')
    

class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('users','recipe')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('users',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'text',
        'pub_date',
        'author',
        'image',
        'cooking_time',
        'get_tags',
        'count_favorites',
        'get_ingredients'
    )
    inlines = (IngredientInline, )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def get_tags(self, obj):
        tags_set = obj.list_tags()
        if tags_set:
            return list(tags_set)
        return None
    
    def count_favorites(self, obj):
        queriset = obj.favorites.count()
        if queriset:
            return queriset
        return None
    
    def get_ingredients(self, obj):
        ingredients_set = obj.list_ingredients()
        if ingredients_set:
            return list(ingredients_set)
        return None


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredintAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Recipe, RecipeAdmin)
