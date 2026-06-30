from django.contrib import admin
from .models import CustomUser, Product, Pack, PackProduct, Cart, Order, CartItem, OrderItem

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Pack)
admin.site.register(PackProduct)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
