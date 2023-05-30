from django.contrib.auth.models import User
from LittleLemonAPI.models import Cart, Order, OrderItem
from decimal import Decimal
from datetime import datetime

def create_order_with_order_items(user):
    carts = Cart.objects.filter(user_id=user.id)
    order = Order.objects.create(
        user=user,
        delivery_crew=None,
        status=0,
        total=Decimal(0),
        date=datetime.now()
    )
    for cart in carts:
        OrderItem.objects.create(
            order=order,
            menuitem=cart.menuitem,
            quantity=cart.quantity,
            unit_price=cart.unit_price,
            price=cart.price
        )
    items = OrderItem.objects.filter(order_id=order.id)
    for item in items:
        order.total += Decimal(item.price)
    order.save()
    carts.delete()
    return items