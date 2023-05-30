from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.http import Http404

from LittleLemonAPI.models import MenuItem, Cart, Order, OrderItem, Category
from LittleLemonAPI.serializers import (MenuItemSerializer, 
                                        CategorySerializer,
                                        UserSerializer, 
                                        CartSerializer,
                                        OrderItemSerializer,
                                        OrderSerializer)
from LittleLemonAPI.paginators import CustomPagination
from LittleLemonAPI.custom_funcs import create_order_with_order_items
from LittleLemonAPI.permissions import IsManager, IsCustomer, IsEmployee


class MenuItemsView(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    ordering_fields = ['price']
    search_fields = ['title']
    filterset_fields = ['category']

    pagination_class = CustomPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'GET':
            permission_classes = []
        elif self.request.method == 'POST':
            if self.request.user.is_superuser:
                permission_classes = [IsAdminUser]
            else:
                permission_classes = [IsManager]
        return [permission() for permission in permission_classes]

    def get_throttles(self):
        if self.request.user.is_authenticated:
            throttle_classes = [UserRateThrottle]
        else:
            throttle_classes = [AnonRateThrottle]
        return [throttle() for throttle in throttle_classes]
    
class MenuItemView(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'GET':
            permission_classes = []
        else:
            if self.request.user.is_superuser:
                permission_classes = [IsAdminUser]
            else:
                permission_classes = [IsManager]
        return [permission() for permission in permission_classes]
    
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'GET':
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class ManagerViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.user.is_superuser:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]

    def add(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response({"message": "user is added to the Manager group successfully"},
                        status=status.HTTP_201_CREATED)
    
    def remove(self, request, pk):
        user = get_object_or_404(User, pk=pk)   
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({"message": "user is removed from Manager group successfully"})
    
class DeliveryCrewViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer

    permission_classes = [IsManager]

    def add(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        delivery_crew = Group.objects.get(name='Delivery crew')
        delivery_crew.user_set.add(user)
        return Response({"message": "user is added to the Delivery Crew group successfully"})
    def remove(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        delivery_crew = Group.objects.get(name='Delivery crew')
        delivery_crew.user_set.remove(user)
        return Response({"message": "user is removed from Delivery Crew group successfully"})
    
class CartView(ListModelMixin, 
               CreateModelMixin, 
               DestroyModelMixin, 
               GenericAPIView):
    serializer_class = CartSerializer

    permission_classes = [IsCustomer]

    def get_queryset(self):
        user = User.objects.get(username=self.request.user.username)
        return Cart.objects.filter(user_id=user.id)
    
    def destroy(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OrderListCreateView(ViewSet):

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = User.objects.get(username=self.request.user.username)
        if user.groups.filter(name="Manager").exists():
            return Order.objects.all()
        elif user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew=user.id)
        else:
            return Order.objects.filter(user_id=user.id)
        
    def list(self, request, *args, **kwargs):
        serialized_items = OrderSerializer(self.get_queryset(), many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        items = create_order_with_order_items(user)
        serialized_items = OrderItemSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_201_CREATED)
    
class OrderRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    ordering_fields = ['price']
    filterset_fields = ['status']

    pagination_class = CustomPagination

    def get_serializer(self, *args, **kwargs):
        if self.request.user.groups.filter(name="Delivery crew").exists():
            kwargs['hidden_fields'] = ['id', 'user', 'delivery_crew', 'total', 'date', 'orderitems']
        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [IsCustomer]
        elif (self.request.method == 'DELETE') or (self.request.method == 'PUT'):
            permission_classes = [IsManager]
        else:
            permission_classes = [IsEmployee]
        return [permission() for permission in permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        pk = kwargs.get('pk', 0)
        try:
            order = get_object_or_404(Order, pk=pk)
        except Http404:
            return Response({"message": "order not found"})
        if user.id != order.user_id:
            return Response({"message": "this order doesn't belong to you"}, \
                            status=status.HTTP_403_FORBIDDEN)
        serialized_item = self.get_serializer(order)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        order_pk = kwargs.get('pk', 0)
        order = get_object_or_404(Order, pk=order_pk)
        if request.user.groups.filter(name="Delivery crew").exists():
            crew_id = User.objects.get(username=request.user.username).id
            if crew_id != order.delivery_crew_id:
                return Response({"message": "this order is not assigned to you"})
        return super().partial_update(request, *args, **kwargs)



    
        
    









    


        



    

