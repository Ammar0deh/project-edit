from django.contrib import admin
from .models import Category, Products, \
     ProductCart, Cart, Client, Order




admin.site.site_header = 'MyStore'
admin.site.index_title = 'MyStore Admin'
admin.site.site_title = 'MyStore'



class ProductInline(admin.StackedInline):
    model = Products
    extra = 0


admin.site.register(Client)
admin.site.register(Order)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [ProductInline,]
admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category','price','available']
    list_filter = ['category', 'available']
admin.site.register(Products, ProductAdmin)



class ProductCartInline(admin.StackedInline):
    model = ProductCart
    extra = 0
    
class CartAdmin(admin.ModelAdmin):
    model = Cart
    inlines = [ProductCartInline,]
admin.site.register(Cart, CartAdmin)