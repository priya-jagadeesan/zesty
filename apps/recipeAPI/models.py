from __future__ import unicode_literals
from django.db import models
from django.db import IntegrityError, transaction
import re
from django.core.files.base import ContentFile

TITLE_REGEX = re.compile(r'^([\w,:\s/-]*)$')

class RecipeManager(models.Manager):
    def validateRecipeTitle(self, postData):
        errors = {}
        try:
            title =  postData.get('header')
        except:
            return {"blank": 'Title is required'}
        
        if not title:
            errors['blank'] = 'Title is required'

        else:
            if len(title) < 3 or len(title) > 16:
                errors['title'] = 'Title: min 3 to 15 characters'
            elif not TITLE_REGEX.match(title):
                errors['title'] = 'Invalid Title'

            if not errors:
                recipes = Recipe.objects.filter(header=title)
                if recipes:
                    errors['title'] =  'Title already exists. Please try another valid title'
        return errors
    @transaction.atomic
    def createRecipeData(self, postData, imageData):
        recipe = Recipe()
        recipe.header = postData.get('header')
        recipe.serves = postData.get('serves')
        recipe.description = postData.get('description')
        recipe.url = postData.get('url')

        if not recipe.description:
            recipe.description = recipe.header
        if not recipe.serves:
            recipe.serves = 1

        if imageData:
            image = imageData.read()
            recipe.image.save(imageData.name, ContentFile(image))
        else:
            recipe.save()
        ingredients = postData.get('ingredients')
        if ingredients:
            for ingr in ingredients:
                Ingredient.objects.create(name = ingr.get('name'), amount = ingr.get('amount'), metric = ingr.get('metric'), recipe = recipe)
        instructions = postData.get('instructions')
        if instructions:
            for step in instructions:
                Instruction.objects.create(step = step.get('step'), recipe = recipe)
        return recipe

    @transaction.atomic
    def updateRecipeData(self, recipe, postData, imageData):
        recipe.header = postData.get('header')
        recipe.serves = postData.get('serves')
        recipe.description = postData.get('description')
        recipe.url = postData.get('url')

        if not recipe.description:
            recipe.description = recipe.header
        if not recipe.serves:
            recipe.serves = 1

        if isinstance(imageData, unicode):
            recipe.save()
        else:
            image = imageData.read()
            recipe.image.save(imageData.name, ContentFile(image))
        
        ingredients = postData.get('ingredients')
        if ingredients:
            recipe.ingredients.all().delete()
            for ingr in ingredients:
                Ingredient.objects.create(name = ingr.get('name'), amount = ingr.get('amount'), metric = ingr.get('metric'), recipe = recipe)
        instructions = postData.get('instructions')
        if instructions:
            recipe.instructions.all().delete()
            for step in instructions:
                Instruction.objects.create(step = step.get('step'), recipe = recipe)
        return recipe
    
class Recipe(models.Model):
    header = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=300)
    serves = models.IntegerField(default=1)
    url = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='images/%Y-%m-%d', default='images/no-img.jpg', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = RecipeManager()

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    amount = models.CharField(max_length=25)
    metric = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recipe = models.ForeignKey(Recipe, related_name = "ingredients", on_delete = models.CASCADE)
    
class Instruction(models.Model):
    step = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    recipe = models.ForeignKey(Recipe, related_name = "instructions", on_delete = models.CASCADE)
