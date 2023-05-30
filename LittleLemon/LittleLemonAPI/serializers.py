from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

from LittleLemonAPI.models import MenuItem, Category, Cart, Order, OrderItem

from decimal import Decimal
from datetime import datetime

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'featured']
        validators = [
            UniqueTogetherValidator(
                queryset=MenuItem.objects.all(),
                fields=['title']
            )
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

        extra_kwargs = {
            'email': {
                'read_only': True,
            }
        }

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']

        read_only_fields = ['unit_price', 'price']

    def save(self, **kwargs):
        menuitem_id = self.context['request'].data.get('menuitem')
        unit_price = MenuItem.objects.get(pk=menuitem_id).price
        quantity = self.context['request'].data.get('quantity')
        price = Decimal(unit_price) * Decimal(quantity)
        kwargs['unit_price'] = unit_price
        kwargs['price'] = price
        super().save(**kwargs)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
            

class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Delivery crew"),
        allow_null=True
    )
    orderitems = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'id', 
            'user', 
            'delivery_crew', 
            'status', 
            'total',
            'date',
            'orderitems',
        ]
        #read_only_fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

        extra_kwargs = {
            'user': {'read_only': True},
            'date': {'read_only': True},
            'total': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):
        hidden_fields = kwargs.pop('hidden_fields', None)

        super().__init__(*args, **kwargs)

        if hidden_fields is not None:
            for field in hidden_fields:
                self.fields.pop(field)

    
    def get_orderitems(self, order: Order):
        order = Order.objects.get(date=order.date)
        items = OrderItem.objects.filter(order_id=order.id)
        return OrderItemSerializer(items, many=True).data
    

        


    
    