from django.contrib.auth.models import User
from django.db import models 
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Products(models.Model):
    category = models.ForeignKey(Category , related_name='products' , on_delete= models.CASCADE)
    name = models.CharField(max_length=255)
    descrption = models.TextField(blank=True , null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='product_image',blank=True,null=True)
    created_by = models.ForeignKey(User , related_name='products', on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)



    #### ADDING THIS :
    
    stock = models.PositiveSmallIntegerField(default=0, null=True, blank=True)

    available = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.stock < 1:
            self.available = False
        else:
            self.available = True
        super().save(*args,**kwargs)


    def __str__(self):
        return self.name
    



    
    ############




class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=750, null=True, blank=True)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        elif self.user.first_name:
            return f'{self.user.first_name}'
        
        elif self.user.last_name:
            return f'{self.user.last_name}'
        else:
            return self.user.username
        
    @property
    def email(self):
        return self.user.email
        
        
    
# Signal function to create a client
@receiver(post_save, sender=User)
def create_client_on_new_user(sender, instance, created, **kwargs):    
    try:
        client = Client.objects.get(user=instance)
    except Client.DoesNotExist:
        client = Client.objects.create(user=instance)
       
    
    
    
    
    
class Cart(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='carts')
    total = models.PositiveIntegerField(default=0, null=True, blank=True)
    done = models.BooleanField(default=False)
    products_q = models.SmallIntegerField(default=0, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True, editable=False)
    payment_code = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        date_time = self.date_created.strftime('%H:%M %d/%m')
        return f'{self.client} Cart - {date_time}'
    
    
       
class ProductCart(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='carts')


    def __str__(self):
        return f'{self.product} ${self.product.price}'
        
    def clean(self):
        if self.product.stock < 1:
            raise ValidationError(f"The quantity requested exceeds the quantity available ({self.product.stock})")
        if self.pk and self.cart.products.filter(id=self.product.id).exists():
            raise ValidationError(f"The product {self.product.name} is allready in the cart")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name_plural = "Shopping Cart Product"
        verbose_name = "Shopping Cart Products"

@receiver(post_save, sender=ProductCart)
@receiver(post_delete, sender=ProductCart)
def update_cart(sender, instance, **kwargs):
    cart = instance.cart
    products = cart.products.all()
    total = 0
    q = 0
    for product in products:
        total += product.product.price
        q += 1
    cart.total = total
    cart.products_q = q    
    cart.save()




 
class Order(models.Model):   
    cart = models.OneToOneField(Cart, related_name="order", on_delete=models.CASCADE)
    
    paid = models.BooleanField(default=False)

    sended = models.BooleanField(default=False)
    
    closed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.paid and self.sended and not self.closed:
            self.closed = True
            self.decrease_product_stock()
        super().save(*args, **kwargs)

    @property
    def client_address(self):
        return self.cart.client.address

    def decrease_product_stock(self):
        products_in_order = self.cart.products.all()
        for product_in_order in products_in_order:
            product = product_in_order.product
            product.stock -= 1
            product.save()
    
    def __str__(self):
        if self.closed == True:
            done = "Done"
        else:
            done = "Not Closed"
        return f'{self.cart.client} Cart - {done}'
    
    
    @property
    def products(self):
        
        cart_products = self.cart.products.all()
        products = []
        for product in cart_products:
            products.append(product.product)
        return products
    
    
    @property
    def total(self):
        
        return self.cart.total
    
    


@receiver(post_save, sender=Cart)
def create_order_on_cart_done(sender, instance, created, **kwargs):
    if instance.done:
        try:         # Check if an Order already exists for this Cart

            order = Order.objects.get(cart=instance)
        except Order.DoesNotExist:
            # Create a new Order for the Cart
            order = Order.objects.create(cart=instance)
            

class Transaction(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='transactions')
    products = models.TextField(default=0)  # Comma-separated list of product names
    payment_code = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f'Transaction for {self.client}'

    def save(self, *args, **kwargs):
        # Replace spaces with underscores in product names before saving
        self.products = ','.join([product.replace(' ', '_') for product in self.product_list])
        super().save(*args, **kwargs)

    @property
    def product_list(self):
        # Return a list of product names for this transaction
        return self.products.split(',')

    @classmethod
    def create_transaction(cls, client, product_list, payment_code=None):
        # Create a new transaction with the given product list and payment code
        products_str = ','.join(product_list)
        return cls.objects.create(client=client, products=products_str, payment_code=payment_code)

    
class BinaryMatrix(models.Model):
    client_id = models.IntegerField(default = 0)
    Nike_Air_Jordan_1_Mid = models.IntegerField(default = 0)
    Nike_Air_Jordan_2_Mid = models.IntegerField(default = 0)
    Nike_Air_Jordan_3_Mid = models.IntegerField(default = 0)

    # Add other fields as needed

    def __str__(self):
        return f'{self.client_id} - {self.Nike_Air_Jordan_1_Mid} - {self.Nike_Air_Jordan_2_Mid} - {self.Nike_Air_Jordan_3_Mid}'

@receiver(post_save, sender=Transaction)
def update_binary_matrix(sender, instance, created, **kwargs):
    if created:
        # Assuming products are unique in the list
        products_purchased = instance.product_list

        # Get or create the BinaryMatrix instance for the client
        binary_matrix, created = BinaryMatrix.objects.get_or_create(client_id=instance.client_id)

        # Set the corresponding product columns to 1 if purchased
        for product in products_purchased:
            product_field_name = f"{product.replace(' ', '_')}"  # Convert product name to field name
            setattr(binary_matrix, product_field_name, 1)

        binary_matrix.save()
post_save.connect(update_binary_matrix, sender=Transaction)



# models.py


class CartProductNames(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_names = models.TextField()

    def __str__(self):
        return f"Cart {self.cart_id} Product Names"
