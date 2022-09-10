from importlib.resources import path
from unittest.mock import patch
from django.urls import path

from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.index, name='index'),
]
