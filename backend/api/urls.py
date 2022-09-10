from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser import views as djoser_views

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='Ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
