import random
from django.core.management.base import BaseCommand
from products.models import BinaryMatrix  # Replace 'your_app' with the actual name of your Django app

class Command(BaseCommand):
    help = 'Generate random transactions in BinaryMatrix table'

    def handle(self, *args, **kwargs):
        # Define the columns you want to generate transactions for
        columns = ['Nike_Air_Jordan_1_Mid', 'Nike_Air_Jordan_2_Mid', 'Nike_Air_Jordan_3_Mid']

        # Generate 500 random transactions
        for _ in range(500):
            transaction_data = {column: random.choice([0, 1]) for column in columns}
            BinaryMatrix.objects.create(**transaction_data)

        self.stdout.write(self.style.SUCCESS('Successfully generated 500 random transactions.'))
