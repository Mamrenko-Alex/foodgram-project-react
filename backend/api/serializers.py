from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredient, 
                            IngredientAmount, Recipe, 
                            ShoppingList, Tag)
from users.models import User, Follow
from .imagefield import ImageConversion


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        followings = Follow.objects.filter(
                    user=user, author=obj)
        return followings.exists()


class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='hexcolor')

    class Meta:
        model = Tag
        fields= ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientAmountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')
    id = serializers.ReadOnlyField(source='ingredients.pk')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ['id', 'amount']


class RecipeSerializers(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        favorite = FavoriteRecipe.objects.filter(
                    user=user, recipe=obj)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        favorite = ShoppingList.objects.filter(
                    user=user, recipe=obj)
        return favorite.exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientWriteSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = ImageConversion(max_length=False, use_url=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = data.get('ingredients')
        ingredients_id = []
        for ingredient in ingredients:
            if  not isinstance(ingredient.get('amount'), int):
                raise serializers.ValidationError(
                    'Значение количество ингредиента (amount) '
                    'должно быть числом. Проверьте и укажите '
                    f'правильное значение {ingredient.get("name")}'
                )
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    'Значение количество ингредиента (amount)'
                    'должно быть больше ноля. Проверьте и укажите '
                    f'правильное значение {ingredient.get("name")}'
                )
            if ingredient['id'] in ingredients_id:
                raise serializers.ValidationError(
                    'Ингредиенты в рецепте не должны повторяться. '
                    'Пожалуйста, проверьте и объедените повторяющиеся '
                    'ингридиенты.'
                )
            ingredients_id.append(ingredient['id'])
        if int(data['cooking_time']) <= 0:
            raise serializers.ValidationError(
                'Время приготовления не может быть равным нолю.'
            )
        return data

    def add_ingredients_and_tag_to_recipe(self, instance, **validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        for tag in tags:
            instance.tags.add(tag)
        for ingredient in ingredients:
            IngredientAmount.objects.bulk_create([
                IngredientAmount(
                    recipe=instance,
                    ingredients_id=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            ])
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags =  validated_data.pop('tags')
        author = validated_data.get('author')
        name = validated_data.get('name')
        recipe = Recipe.objects.filter(author=author, name=name)
        if recipe.exists():
            raise serializers.ValidationError(
                'У вас уже есть рецепт с таким названием'
            )
        recipe = Recipe.objects.create(
            **validated_data
        )
        return self.add_ingredients_and_tag_to_recipe(
            recipe,
            ingredients=ingredients,
            tags=tags
        )
    
    def update(self, instance, validated_data):
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = self.add_ingredients_and_tag_to_recipe(
            instance,
            ingredients=ingredients,
            tags=tags
        )
        return super().update(instance, validated_data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
            source='author.recipes.count', 
            read_only=True
    )

    class Meta:
        model = Follow
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        followings = Follow.objects.filter(
                    user=obj.user, author=obj.author)
        return followings.exists()

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return FavoriteRecipeSerializer(queryset, many=True).data
