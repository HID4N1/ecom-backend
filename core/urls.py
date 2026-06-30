from django.urls import path
from .views import UserList, UserDetail, ProductList, ProductDetail, CartDetail, OrderList, OrderDetail, \
    RegisterView, LogoutView, CommerceDataView, PackList, PackDetail

urlpatterns = [
    path('commerce', CommerceDataView.as_view(), name='commerce-data-no-slash'),
    path('commerce/', CommerceDataView.as_view(), name='commerce-data'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout-no-slash'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('products', ProductList.as_view(), name='product-list-no-slash'),
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('packs', PackList.as_view(), name='pack-list-no-slash'),
    path('packs/', PackList.as_view(), name='pack-list'),
    path('packs/<int:pk>/', PackDetail.as_view(), name='pack-detail'),
    path('cart/', CartDetail.as_view(), name='cart-detail'),
    path('orders/', OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
]
