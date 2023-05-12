from rest_framework import serializers as serializers

from .models import Recipe


class RecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        # depth = 2
