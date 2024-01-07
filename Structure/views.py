from products.models import Category, Products
from django.shortcuts import render , redirect
from .forms import SignupForm





def home(request):
    categories = Category.objects.all()
    products = Products.objects.all()
    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
    })


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'signup.html',
                    {'form': form
                     })


def test_page(request):
    categories = Category.objects.all()
    products = Products.objects.all()

    context = {
        'categories': categories,
        'products': products,
        # Add more key-value pairs as needed
    }

    return render(request, 'test_page.html', context)