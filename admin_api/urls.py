from django.urls import path
from .views import *



urlpatterns = [

    path('list-users/', ListUsersAPIView.as_view(), name='list-users'),
    path('user-details/<int:pk>/',UserDetailsAdmin.as_view(), name='user_details'),


    path('create-list-categories/', CategoryCreateView.as_view(), name='create_list_category'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), 
         name='category-retrieve-update-destroy'),



    path('product-list-create/', ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), 
         name='product_retrieve_update_destroy'),
    path('products/<int:pk>/delete_review/<int:review_id>/', DeleteProductReviewView.as_view(), 
         name='admin_delete_product_review'),



    path('admin-orders/', OrderListView.as_view(), name='admin_order_list'),
    path('admin-orders/<int:pk>/', OrderDetailsView.as_view(), name='admin_order_details'),

    path('send-promo-email/', SendPromotionalEmailView.as_view(), name='send_promotional_email'),
    
]