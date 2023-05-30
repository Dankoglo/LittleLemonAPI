from django.urls import path

from LittleLemonAPI import views

urlpatterns = [
    path('menu-items/', views.MenuItemsView.as_view(), name='menu-items'),
    path('menu-items/<int:pk>/', views.MenuItemView.as_view(), name='menu-item'),
    path('categories/', views.CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='categories'),
    path(
        'categories/<int:pk>/', 
        views.CategoryViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), 
        name='category'
    ),
    path(
        'groups/manager/users/', 
        views.ManagerViewSet.as_view({'get': 'list', 'post': 'add'}), 
        name='managers'
    ),
    path(
        'groups/manager/users/<int:pk>/', 
        views.ManagerViewSet.as_view({'delete': 'remove'}), 
        name='remove-from-managers'
    ),
    path(
        'groups/delivery-crew/users/',
        views.DeliveryCrewViewSet.as_view({'get': 'list', 'post': 'add'}),
        name='delivery-crew-users' 
    ),
    path(
       'groups/delivery-crew/users/<int:pk>/',
       views.DeliveryCrewViewSet.as_view({'delete': "remove"}),
       name='remove-from-delivery-crew' 
    ),
    path('cart/menu-items/', views.CartView.as_view(), name='cart'),
    path('orders/', views.OrderListCreateView.as_view({'get': 'list', 'post': 'create'}), name='orders'),
    path(
        'orders/<int:pk>/', 
        views.OrderRetrieveUpdateDeleteView.as_view(),
        name='order'
    ),
]