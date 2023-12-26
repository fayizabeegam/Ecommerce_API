from django.urls import path,include
from .views import *
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('login/',Login.as_view(), name='login'),
    path('register/',UserRegisterView.as_view(), name='userregister'),

    path('user-details/<int:user_id>/', UserDetailAPIView.as_view(), name='user_details'),


    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    

    path('list-categories/', ListCategory.as_view(), name='list_category'),
    path('product-list-search/', ListSearchProduct.as_view(), name='product_list_search'),


    path('product-details/<int:product_id>/', ProductDetails.as_view(), name='product_details'),
    path('product-details/<int:product_id>/create/review/', CreateProductReview.as_view(),
          name='create_product_review'),
   

    path('refreshtoken/', jwt_views.TokenRefreshView.as_view(), name='refreshtoken'),
    path('access_token/', jwt_views.TokenObtainPairView.as_view(), name='access_token'),
]