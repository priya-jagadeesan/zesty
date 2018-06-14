from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializer import *
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.shortcuts import redirect
import ast
from django.http.multipartparser import MultiPartParser


class RecipeList(APIView):
    def get(self, request, format=None):
        recipes = Recipe.objects.order_by('-id')
        data = RecipeSerializer(recipes, many=True)
        return Response(data.data)
    
class RecipeData(APIView):
    def get_object(self, pk):
        try:
            return Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        recipe = self.get_object(pk)
        if recipe:
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        recipe = self.get_object(pk)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        recipe = self.get_object(pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
def create(request):
    data = {}
    data['header'] = request.POST.get('header')
    data['serves'] = request.POST.get('serves')
    data['url'] = request.POST.get('url')
    data['description'] = request.POST.get('description')
    data['image'] = request.FILES.get('image')
    data['ingredients'] = json.loads(request.POST.get('ingredients'))
    data['instructions'] = ast.literal_eval(request.POST.get('instructions'))
    validTitle = Recipe.objects.validateRecipeTitle(data)
    if not validTitle:
        createRecipe = Recipe.objects.createRecipeData(data, data['image'])
        return redirect ('/recipe')
    else:
        return JsonResponse({'error': validTitle})

@csrf_exempt
def update(request, pk):
    try:
        recipe = Recipe.objects.get(id=pk)
    except Recipe.DoesNotExist:
        return JsonResponse({'error': 'choose a valid Recipe'})
    parser = MultiPartParser(request.META, request, request.upload_handlers)
    POST, FILES = parser.parse()
    data = {}
    data['header'] = POST.get('header')
    data['serves'] = POST.get('serves')
    data['url'] = POST.get('url')
    data['description'] = POST.get('description')
    data['ingredients'] = json.loads(POST.get('ingredients'))
    data['instructions'] = json.loads(POST.get('instructions'))
    if not FILES.get('image'):
        data['image'] = POST.get('image')
    else:
        data['image'] = FILES.get('image')
    recipe = Recipe.objects.updateRecipeData(recipe, data, data['image'])
    return redirect('/recipe/' + str(pk))