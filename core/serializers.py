from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Pack, PackProduct, Cart, CartItem, OrderItem, Order

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'address', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'address', 'phone_number')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PackProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = PackProduct
        fields = ('id', 'product', 'quantity', 'order')


class PackSerializer(serializers.ModelSerializer):
    price_value = serializers.SerializerMethodField()
    price_label = serializers.SerializerMethodField()
    products = PackProductSerializer(source='pack_products', many=True, read_only=True)

    class Meta:
        model = Pack
        fields = (
            'id',
            'title',
            'description',
            'price',
            'price_value',
            'price_label',
            'cta',
            'includes',
            'products',
            'created_at',
            'updated_at',
        )

    def get_price_value(self, obj):
        return int(obj.price)

    def get_price_label(self, obj):
        return f"{int(obj.price)} DH"


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

    def create(self, validated_data):
        product_instance = validated_data.pop('product')
        # Use product_instance attributes directly for get_or_create
        product_instance, created = Product.objects.get_or_create(
            id=product_instance.id,
            defaults={
                'name': product_instance.name,  # Example: Replace with actual fields
                'description': product_instance.description  # Example: Replace with actual fields
                # Add other fields as needed
            }
        )
        cart_item = CartItem.objects.create(product=product_instance, **validated_data)
        return cart_item

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'created_at', 'updated_at', 'user')
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')

    def create(self, validated_data):
        items_data = validated_data.pop('items', None)
        cart = Cart.objects.create(**validated_data)
        if items_data:
            for item_data in items_data:
                cart_item = CartItem.objects.create(**item_data)
                cart.items.add(cart_item)
        return cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        if items_data is not None:
            instance.items.all().delete()
            instance.items.clear()
            for item_data in items_data:
                cart_item = CartItem.objects.create(**item_data)
                instance.items.add(cart_item)

        return instance
    # def update(self, instance, validated_data):
    #     items_data = validated_data.pop('items', None)
    #     if items_data:
    #         instance.items.clear()  # Clear existing items before adding updated ones
    #         for item_data in items_data:
    #             product_data = item_data.pop('product')
    #             product_id = product_data.id
    #             quantity = item_data.get('quantity')
    #             product_instance = Product.objects.get(pk=product_id)
    #             instance.items.create(product=product_instance, quantity=quantity)
    #     return instance


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('user', 'total_price', 'created_at', 'updated_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(total_price=0, **validated_data)
        total_price = 0

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = item_data.get('price') or product.price
            order_item = OrderItem.objects.create(
                product=product,
                quantity=quantity,
                price=price,
            )
            order.items.add(order_item)
            total_price += price * quantity

        if items_data:
            order.total_price = total_price
            order.save(update_fields=['total_price'])

        return order
