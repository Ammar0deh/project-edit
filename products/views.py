from django.shortcuts import render , get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from products.forms import ClientForm, CartForm
from .models import Products, \
                    Cart, ProductCart, Client, Order ,Transaction,CartProductNames
from recommendations.models import Result
from itertools import groupby

############################################
import xml.etree.ElementTree as ET

def get_client_transactions(request, client_id):
    client = Client.objects.filter(id=client_id).first()
    transactions = Order.objects.filter(cart__client=client)

    transactions_by_category = {}

    for transaction in transactions:
        cart = transaction.cart
        for product_cart in cart.products.all():
            category = product_cart.product.category.name  
            if category not in transactions_by_category:
                transactions_by_category[category] = []
            transactions_by_category[category].append(transaction)

    root = ET.Element("transactions")

    for category, category_transactions in transactions_by_category.items():
        category_element = ET.SubElement(root, "category", name=category)
        for transaction in category_transactions:
            transaction_element = ET.SubElement(category_element, "transaction", id=str(transaction.id))
            for product_cart in transaction.cart.products.all():
                product_element = ET.SubElement(transaction_element, "product")
                ET.SubElement(product_element, "name").text = product_cart.product.name
    tree = ET.ElementTree(root)

    tree.write("transactions.xml", encoding="utf-8", xml_declaration=True)

    return HttpResponse("XML exported successfully.")





############################################

def detail (request , pk) :
    product = get_object_or_404(Products , pk=pk)
    related_products = Products.objects.filter(category=product.category).exclude(pk=pk)[0:3]

    return render(request, 'Products/detail.html' , {

         'product' : product ,
         'related_products' : related_products ,
    })


def product_list(request):
    products = Products.objects.all()  
    return render(request, 'structure/test_page.html', {'products': products})



############################################


##########################
################################## Cart and shopping logic

def add_product_into_cart(request, product_id):
    client = request.user.client
    cart, created = Cart.objects.get_or_create(client=client, done=False)
    try:
        product = Products.objects.get(pk=product_id)
        product_cart, created = ProductCart.objects.get_or_create(cart=cart, product=product)
          
        return redirect('cart')
    
    except Products.DoesNotExist:
        context = {
            'error': 'Ups! Something gets wrong, please try again or contact the webmaster. Thanks!'
        }
        return redirect('home')

def delete_cart_product(request, product_cart_id):
    product_cart = ProductCart.objects.filter(id=product_cart_id).first()
    if product_cart:
        product_cart.delete() ## AJAX HERE
    return redirect(reverse('cart')+ "?deleted")


def cart(request):
    client = request.user.client
    try:
        cart = Cart.objects.get(client=client, done=False)
        context = {
            'cart' : cart,
            'client': client,
        }
        template_name = 'cart.html'
        return render(request, template_name, context)
    
    except Cart.DoesNotExist:
        cart = Cart.objects.create(client=client, done=False)
        context = {
            'cart' : cart,
            'client': client,
        }
        template_name = 'cart.html'
        return render(request, template_name, context)
    
def checkout(request, cart_id):
    cart = Cart.objects.filter(id=cart_id).first()
    if request.method == 'GET':
        client_form = ClientForm(instance=cart.client)
        cart_form = CartForm(instance=cart)
        context = {
        'cart' : cart,
        'client_form': client_form,
        'cart_form': cart_form,
        }

        template_name = 'checkout.html'
        return render(request, template_name, context)
    if request.method == 'POST':
        if 'client_form' in request.POST:
            client_form = ClientForm(request.POST, instance=cart.client)
            if client_form.is_valid():
                updated_client = client_form.save()
        if 'cart_form' in request.POST:
            cart_form = CartForm(request.POST, instance=cart)
            if cart_form.is_valid():
                updated_cart = cart_form.save()
                updated_cart.done = True
                updated_cart.save()

                # Assuming you have a payment_code variable from your payment processing logic
                payment_code = cart.payment_code

                # Get the product list from the cart
                product_list = [str(product.product) for product in updated_cart.products.all()]

                # Create a new transaction
                transaction = Transaction.create_transaction(client=updated_cart.client, product_list=product_list, payment_code=payment_code)

        return redirect('checkout', cart.id)
    




def reco_cart(request):
    # Retrieve data from CartProductNames
    cart_product_names = CartProductNames.objects.all()

    all_product_names = set()
    recommendations = set()

    # Debugging: Print information about CartProductNames
    print("CartProductNames:")
    for cart_product in cart_product_names:
        # Collect all product names from CartProductNames
        product_names = cart_product.product_names.split(', ')
        print(cart_product.cart_id, product_names)
        all_product_names.update(product_names)

    # Query recommendations for all product names
    antecedent_matches = Result.objects.filter(antecedent__overlap=list(all_product_names))

    # Debugging: Print information about Recommendations
    print("All Product Names:", all_product_names)
    print("Recommendations:")
    for match in antecedent_matches:
        consequent_ids = match.consequent
        if consequent_ids:
            consequent_names = Products.objects.filter(id__in=consequent_ids).values_list('name', flat=True)
            print(consequent_names)
            recommendations.update(consequent_names)

    return render(request, 'cart.html', {'all_product_names': all_product_names, 'recommendations': recommendations})





