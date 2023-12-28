from accounts.models import *
from .serializers import *
from django.db import IntegrityError
from rest_framework import generics, permissions, status, filters
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from accounts.serializers import *
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .signals import send_promotional_email
from django.shortcuts import render




class ListUsersAPIView(ListAPIView):
    """
       Admin can list all users
    """
    queryset = CustomUser.objects.all()
    serializer_class = ListUsersSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']



class UserDetailsAdmin(generics.RetrieveUpdateDestroyAPIView):

    """
       Admin can get the user and manage user
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = CustomUser.objects.filter(status=0)
    lookup_field = "pk"
 
    def get_object(self):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(CustomUser, id=user_id)
 
        # Check if the user making the request is an admin user
        if not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to access this user's details.")
 
        return user
 
    def get(self, request, pk, format=None):
        instance = self.get_object()
        serializer = UserDetailSerializer(instance)
        return Response(serializer.data)
 
    def patch(self, request, pk, format=None):
        instance = self.get_object()
        serializer = UserDetailSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Successfully patched!",
                "body": serializer.data,
            }, status=200)
 
        return Response(serializer.errors, status=400)
 
    def delete(self, request, pk, format=None):
        user = self.get_object()
        try:
            user.delete()
            return Response({
                "Status": "Success",
                "Message": "User deleted"
            }, status=204)
        except:
            return Response({
                "Status": "Failed",
                "Message": "Deletion Failed"
            }, status=500)




class CategoryCreateView(generics.ListCreateAPIView):

    """
       Admin can add new categories
    """
 
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get_serializer_class(self):
        return CategorySerializer
 
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
 
            self.perform_create(serializer)
            return Response({"message": "New Category Added successfully", "data": serializer.data},
                             status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"message": "Category with the same name already exists"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
 
    def perform_create(self, serializer):
        serializer.save()


 
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
       Admin can retrieve existing categories and manage categories
    """
 
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            instance = self.get_object()
            serializer = CategorySerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                "Status": "Not Found",
                "Message": "Category does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
 
    def put(self, request, pk, format=None):
        instance = self.get_object()
        serializer = CategorySerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Successfully Updated!",
                "body": serializer.data,
            }, status=200)
 
 
    def patch(self, request, pk, format=None):
        instance = self.get_object()
        serializer = CategorySerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Successfully patched!",
                "body": serializer.data,
            }, status=200)
 
 
    def delete(self, request, pk, format=None):
        category = self.get_object()
        try:
            category.delete()
            return Response({
                "Status": "Success",
                "Message": "Category deleted"
            }, status=204)
        except:
            return Response({
                "Status": "Failed",
                "Message": "Category Deletion Failed"
            }, status=500)
        



class ProductListCreateView(generics.ListCreateAPIView):

    """
       Admin can add new products and list products
    
    """
    queryset = Product.objects.all()
    serializer_class = CreateProductSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
 
    def get_serializer_class(self):
        return CreateProductSerializer
 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        self.perform_create(serializer)
        return Response({"message": "New Product Added successfully", "data": serializer.data}, 
                        status=status.HTTP_201_CREATED)
 
    def perform_create(self, serializer):
        serializer.save()
 



class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    """ 
      Admin can retrieve products and manage products
    
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
 
    def get(self, request, pk, format=None):
        try:
            instance = self.get_object()
            serializer = ProductSerializer(instance)
            return Response({
                "status": "success",
                "message": "Product details retrieved successfully",
                "body": serializer.data,
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                "status": "not found",
                "message": "Product does not exist",
            }, status=status.HTTP_404_NOT_FOUND)
 
    def put(self, request, pk, format=None):
        instance = self.get_object()
        serializer = ProductSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            categories_data = serializer.validated_data.pop('categories', '')
 
            category_ids = [int(cat_id.strip()) for cat_id in categories_data.split(',') 
                            if cat_id.strip()]
            
            # Update categories for the product using set()
            instance.categories.set(category_ids)

            # Save the updated product without assigning 'categories'
            serializer.save()
 
            return Response({
                "status": "success",
                "message": "Successfully Updated!",
                "body": serializer.data,
            }, status=200)
 
    def patch(self, request, pk, format=None):
        instance = self.get_object()
        serializer = ProductSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            categories_data = serializer.validated_data.pop('categories', '')
            category_ids = [int(cat_id.strip()) for cat_id in categories_data.split(',') 
                            if cat_id.strip()]
            instance.categories.set(category_ids)
            serializer.save()
            category_details = CategorySerializer(instance.categories.all(), many=True).data
            serializer.data['category_details'] = category_details
 
            return Response({
                "status": "success",
                "message": "Successfully patched!",
                "body": serializer.data,
            }, status=200)
 
        return Response({
            "status": "error",
            "message": "Invalid data",
            "body": serializer.errors,
        }, status=400)    
   
 
    def delete(self, request, pk, format=None):
        category = self.get_object()
        try:
            category.delete()
            return Response({
                "Status": "Success",
                "Message": "Product deleted"
            }, status=204)
        except:
            return Response({
                "Status": "Failed",
                "Message": "product Deletion Failed"
            }, status=500)




class DeleteProductReviewView(generics.DestroyAPIView):
    """ 
      Admin can delete product reviews posted the user
    
    """

    queryset = Review.objects.all()
    serializer_class = DeleteReviewSerializer
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk, review_id, format=None):
        serializer = self.get_serializer(data={"review_id": review_id})
        serializer.is_valid(raise_exception=True)

        review_to_delete = get_object_or_404(Review, pk=serializer.validated_data["review_id"], 
                                             product__pk=pk)

        review_to_delete.delete()

        return Response({"message": "Review deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



 
class OrderListView(generics.ListAPIView):
    """
       Admin can list all orders from the user
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]



class OrderDetailsView(generics.RetrieveAPIView):

    """
       Admin can view the order details and set status of order
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        serializer = UpdateOrderStatusSerializer(order, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order status updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        serializer = UpdateOrderStatusSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order status updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPromotionalEmailView(APIView):
    """
      Admin can send promotional emails to all users
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        existing_users = CustomUser.objects.all()

        for user in existing_users:
            send_promotional_email(sender=None, instance=user, created=False)
 
        return render(request, 'promo_email.html')


