from csv import reader

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients data from csv-file to DB."

    def handle(self, *args, **kwargs):
        with open(
            f"{settings.BASE_DIR}/ingredients.csv", "r", encoding="UTF-8"
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
