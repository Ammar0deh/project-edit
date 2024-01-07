# products/management/commands/delete_binary_matrix.py
from django.core.management.base import BaseCommand
from products.models import BinaryMatrix 
from recommendations.models import Result

class Command(BaseCommand):
    help = 'Deletes all data from the BinaryMatrix model'

    def handle(self, *args, **options):
        # Delete all data from BinaryMatrix
        Result.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Data deleted from BinaryMatrix model.'))
