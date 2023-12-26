from django.urls import path
from .views import *



urlpatterns = [
     

    path('cart/', CartView.as_view(), name='cart'),
    path('cart-items/', CartItemView.as_view(), name='cart_items'),
    path('cart-items/<int:pk>/', CartItemDetailView.as_view(), name='cart_item_detail'),


    path('create-address/', AddressCreateView.as_view(), name='create_address'),
    path('update-delete-address/<int:pk>/', AddressDetailView.as_view(), name='create_delete_address'),
    
    
    path('order-user-review/', OrderUserReviewView.as_view(), name='order_use_review'),
    path('place-order/', OrderPlaceView.as_view(), name='place_order'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
]