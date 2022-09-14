from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingList, Tag)
from users.models import Follow, User
from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveViewSet
from .pagination import LimitPageNumberPagination
from .permissions import AdminUserOrReadOnly
from .services import create_shopping_list

from .serializers import (FavoriteRecipeSerializer, FollowSerializer,
                         IngredientAmountSerializer, IngredientSerializer,
                         RecipeSerializers, RecipeWriteSerializer,
                         TagSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username')

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_profile(self, request):
        user = get_object_or_404(self.queryset, pk=request.user.pk)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        user = get_object_or_404(self.queryset, pk=request.user.pk)
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        if new_password == current_password:
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def subscribe(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.pk)
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if user is author:
                return Response(
                    {'errors' : 'Вы не можете подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.filter(user=user, author=author)
            if follow.exists():
                return Response(
                    {'error' : 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.create(user=user, author=author)
            serializers = FollowSerializer(
                follow, context={'request' : request})
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user is author:
                return Response(
                    {'errors' : 'Вы не можете отписаться от самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.filter(user=user, author=author)
            if not follow.exists():
                return Response(
                    {'error' : 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter


class IngredientAmountViewSet(viewsets.ModelViewSet):
    queryset = IngredientAmount.objects.all()
    serializer_class = IngredientAmountSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    permission_classes = (AdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializers
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def favorite(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.pk)
        recipe = get_object_or_404(Recipe, pk=pk)
        favorited = FavoriteRecipe.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if favorited.exists():
                return Response(
                    {'error' : 'Вы уже добавили рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorited = FavoriteRecipe.objects.create(
                user=user, recipe=recipe)
            serializers = FavoriteRecipeSerializer(
                recipe, context={'request' : request})
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not favorited.exists():
                return Response(
                    {'error' : 'Этого рецепта не в вашем списке избраного.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorited.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def shopping_cart(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.pk)
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping = ShoppingList.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if in_shopping.exists():
                return Response(
                    {'error' : 'Вы уже добавили рецепт в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            in_shopping = ShoppingList.objects.create(
                user=user, recipe=recipe)
            serializers = FavoriteRecipeSerializer(
                recipe, context={'request' : request})
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not in_shopping.exists():
                return Response(
                    {'error' : 'У вас нет этого рецепта в списоке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            in_shopping.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def get_shopping_card(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_list__user=user).values(
            'ingredients__name',
            'ingredients__measurement_unit').order_by(
            'ingredients__name').annotate(total=Sum('amount'))
        return create_shopping_list(ingredients)
