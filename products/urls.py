from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/' , views.detail ,name='product_detail') ,
    path('', views.product_list, name="product_list"), 
    path('transactions/<int:client_id>/', views.get_client_transactions, name="transactions"),
]