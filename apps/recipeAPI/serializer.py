from rest_framework import serializers
from .models import *
import re
from drf_writable_nested import WritableNestedModelSerializer

TITLE_REGEX = re.compile(r'^([\w,:\s/-]*)$')

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'amount', 'metric')

class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ('step',)

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'header', 'description', 'serves', 'url', 'image', 'ingredients', 'instructions')



class RecipeCreateSerializer(WritableNestedModelSerializer):
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)
    # image = serializers.ImageField(max_length=None, allow_empty_file=True, use_url=True)
    class Meta:
        model = Recipe
        fields = ('id', 'header', 'description', 'serves', 'url', 'image', 'ingredients', 'instructions')

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title is required.")
            return value
        if len(value) < 3:
            raise serializers.ValidationError("Title is required. Min 3chars.")
            return value
        if not TITLE_REGEX.match(value):
            raise serializers.ValidationError("Invalid Title. Try avoiding special characters.")
            return value

class RecipeUpdateSerializer(WritableNestedModelSerializer):
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('header', 'description', 'serves', 'url', 'image', 'ingredients', 'instructions')
        # extra_kwargs = {
        #     'header': {'validators': []},
        # }