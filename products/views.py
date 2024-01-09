import json
from django.shortcuts import render , get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from products.forms import ClientForm, CartForm
from .models import Products, \
                    Cart, ProductCart, Client, Order ,Transaction ,Category , LiveCart ,ResultCons
from association_rules.models import Result
from itertools import groupby
from django.db.models import Q
from django.http import JsonResponse
############################################
import xml.etree.ElementTree as ET
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore

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
    template_name = 'checkout.html'
    context = {'cart': cart}

    if request.method == 'GET':
        # Fetch associated products
        associated_products = recommend_products(cart)
        context['associated_products'] = associated_products

        client_form = ClientForm(instance=cart.client)
        cart_form = CartForm(instance=cart)
        context.update({
            'client_form': client_form,
            'cart_form': cart_form,
        })

        return render(request, template_name, context)

    elif request.method == 'POST':
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

    
def browse(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    products = Products.objects.filter(available=True)  # Use 'products' instead of 'browse'

    if category_id:
        products = products.filter(category_id=category_id)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(descrption__icontains=query))

    return render(request, 'browse.html', {  # Correct template name and variable name
        'products': products,  # Correct variable name
        'query': query,
        'categories': categories,
        'category_id': int(category_id)
    })
def recommend_products(request, cart):
    # Fetch the LiveCart object based on the client
    live_cart = LiveCart.objects.filter(cart_id=cart.id).first()
    print("Live Cart:", live_cart)

    # Convert live_cart.product_names to a list
    product_names_list = json.loads(live_cart.product_names)
    print("Product Names List:", product_names_list)

    # Fetch the association rule for the given live_cart
    association_rule = Result.objects.filter(antecedent__contains=product_names_list).first()
    print("Association Rule:", association_rule)

    recommended_products = []

    if association_rule:
        # Check if the antecedent in the association rule matches the product_names_list
        if all(product in association_rule.antecedent for product in product_names_list):
            # Fetch the consequent from the association rule
            consequent_products = association_rule.consequent.split(', ')
            print("Consequent Products:", consequent_products)

            # Save the consequent and cart_id in the ResultCons model
            result_cons = ResultCons.objects.create(cart_id=cart.id, consequent=', '.join(consequent_products))
            result_cons.save()

            # Assuming there is a Product model with 'name', 'image', 'price', and 'description' fields
            recommended_products = Products.objects.filter(name__in=consequent_products)
            print("Recommended Products:", recommended_products)

            # Store recommendations in the user's session
            user_id = request.user.id if request.user.is_authenticated else None
            session_key = request.session.session_key

            if user_id and session_key:
                # Create a custom key based on user_id and session_key
                recommendations_key = f"recommendations_{user_id}_{session_key}"

                # Store recommendations in the session
                request.session[recommendations_key] = list(recommended_products.values_list('name', flat=True))
                print("Product Names in Products Model:", Products.objects.filter(name__in=consequent_products).values_list('name', flat=True))

    return recommended_products










def cart_view(request):
    cart = LiveCart.objects.get(user=request.user)
    print("Cart ID:", cart.id)
    print("Product Names:", cart.product_names)  # Check if product_names contains the expected data

    # Call the recommend_products function to get recommendations
    recommendations = recommend_products(request, cart)

    # Render the cart.html template with the cart and recommendations
    return render(request, 'cart.html', {'cart': cart, 'recommendations': recommendations})





