import datetime
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http.response import Http404
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import filters,status
from rest_framework.generics import ListAPIView,RetrieveUpdateDestroyAPIView
from .models import *
from .serializers import  *
from admin_api.serializers import *
from rest_framework.filters import *
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination


# Create your views here.


class UserRegisterView(generics.CreateAPIView):
    """
       User can register account
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "User registered successfully", "data": serializer.data}, 
                        status=status.HTTP_201_CREATED)
 
       
    def perform_create(self, serializer):
        serializer.save()
    


class Login(generics.ListAPIView):
    """
      User login view
    
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    
 
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                user_obj = CustomUser.objects.get(
                    Q(username__iexact=data["username"]) | Q(email__iexact=data["username"])
                )
               
                # Check if the user is active
                if user_obj.status == 0:
                    if check_password(data["password"], user_obj.password):
                        user_obj.last_login = datetime.datetime.now()
                        user_obj.save()
                        refresh_token = RefreshToken.for_user(user_obj)
                        resp = LoginResponseSerializer(instance=user_obj)
                        return Response(resp.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Invalid password", "status": "1"})
                else:
                    return Response({"message": "you are blocked by admin"})
 
            except CustomUser.DoesNotExist:
                return Response({"message": "Invalid user", "status": "1"})
               
            except Exception as e:
                print("Login error:", str(e))
                return Response({"message": "An error occurred", "status": "1"})
        else:
            return Response(serializer.errors)




class UserDetailAPIView(RetrieveUpdateDestroyAPIView):
    """ 
      User can manage their details
    
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
 
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = CustomUser.objects.get(id=user_id)
 
        # Check if the user making the request is the same as the user whose details are being accessed
        if self.request.user.id == user.id:
            return user
        else:
            raise PermissionDenied("You do not have permission to access this user's details.")
 
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
 
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
                "status": "success",
                "message": "Successfully updated!",
                "body": serializer.data,
            }, status=200)
    
    
    def delete(self, request, *args, **kwargs):
       
        try:
            user = self.get_object()
            user.delete()
            # details.delete()
            return Response(
                {
                    "Status" : "succes",
                    "Message" : "deleted"
                }
            )
        except:
            return Response(
                {
                    "Status" : "Failed",
                    "Message" : " deletion failed"
                }
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class ListCategory(ListAPIView):
    """
       User can list available categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['Category_id','category_name',]



class ListProductPagination(PageNumberPagination):
    page_size = 5

class ListSearchProduct(ListAPIView):
    """
       User can search products based on category and product name etc
    
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter,]
    search_fields = ['product_name','price','categories__category_name']
    pagination_class = ListProductPagination
 
    def get_queryset(self):
        queryset = super().get_queryset()
 
     
        price= self.request.query_params.get('price', None)
        product_name = self.request.query_params.get('product_name',None)
        category_name = self.request.query_params.get('category_name', None)
       
        price_from = self.request.query_params.get('price_from', None)
        price_to = self.request.query_params.get('price_to', None)
 
 
        # If price is provided, filter the queryset
        if price is not None:
            try:
                price = int(price)
                queryset = queryset.filter(price=price)
            except ValueError:
                raise Http404("Invalid price provided")
           
        if price_from is not None and price_to is not None:
            try:
                price_from = float(price_from)
                price_to = float(price_to)
                queryset = queryset.filter(price__range=[price_from, price_to])
            except ValueError:
                raise Http404("Invalid price range provided")
           
        if product_name is not None:
            try:
                product_name = str(product_name)
                queryset = queryset.filter(product_name__icontains=product_name)            
            except ValueError:
                raise Http404("Invalid product_name provided")
           
        if category_name is not None:
            try:
                queryset = queryset.filter(categories__category_name__icontains=category_name)
            except ValueError:
                raise Http404("Invalid category_name provided")
 
        return queryset
    


class ProductDetails(generics.RetrieveAPIView):
    """
        User can view the details of the products
    """
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'product_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request,args, **kwargs)


        return response
    


class CreateProductReview(generics.CreateAPIView):
    """
       User can add review for products
    """
    serializer_class = CreateReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        product_id = self.kwargs.get('product_id')
        return get_object_or_404(Product, pk=product_id)

    def perform_create(self, serializer):
        product = self.get_object()
        serializer.save(user=self.request.user, product=product) 