# Generated by Django 2.2.19 on 2022-09-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20220911_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.IngredientAmount', to='recipes.Ingredient', verbose_name='Ингридиенты'),
        ),
    ]
