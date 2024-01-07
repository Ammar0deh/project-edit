
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from products.views import cart, add_product_into_cart, delete_cart_product, \
                            checkout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Structure.urls')),
    path('products/', include('products.urls')),
    path('cart/', login_required(cart), name="cart"),
    path('cart/add/<int:product_id>/', login_required(add_product_into_cart), name="add_product"),
    path('cart/delete/<int:product_cart_id>/', login_required(delete_cart_product), name="delete_product"),
    path('checkout/<int:cart_id>/', login_required(checkout), name="checkout"),
    path('recommendations/', include('recommendations.urls')),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


