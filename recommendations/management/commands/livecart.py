# your_app/management/commands/populate_cart_product_names.py
from django.core.management.base import BaseCommand
from products.models import CartProductNames, ProductCart, Products

class Command(BaseCommand):
    help = 'Populate CartProductNames with product names based on ProductCart data'

    def handle(self, *args, **options):
        # Clear existing CartProductNames data
        CartProductNames.objects.all().delete()

        # Get unique cart IDs
        cart_ids = ProductCart.objects.values('cart_id').distinct()

        for cart_id_entry in cart_ids:
            cart_id = cart_id_entry['cart_id']
            product_ids = ProductCart.objects.filter(cart_id=cart_id).values_list('product_id', flat=True)
            product_names = [Products.objects.get(id=product_id).name for product_id in product_ids]

            # Create CartProductNames entry
            CartProductNames.objects.create(cart_id=cart_id, product_names=', '.join(product_names))

        self.stdout.write(self.style.SUCCESS('CartProductNames successfully populated.'))
