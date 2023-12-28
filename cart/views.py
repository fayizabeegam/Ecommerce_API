from .serializers import *
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.db import IntegrityError
from rest_framework import filters,status
from django.http.response import Http404
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView


# Create your views here.



class CartView(generics.RetrieveAPIView):
    """
       creating a cart for user
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_object(self):
        return Cart.objects.get_or_create(user=self.request.user)[0]



class CartItemView(generics.ListCreateAPIView):
    """
       user can add items in to cart and view the added items in the cart
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
 
    def perform_create(self, serializer):
        cart = Cart.objects.get_or_create(user=self.request.user)[0]
 
        if 'product' not in self.request.data:
            raise serializers.ValidationError("Product data is required.")
 
        product_id = self.request.data['product']
        product = Product.objects.get(pk=product_id)
 
        serializer.save(cart=cart, product=product, added_by=self.request.user)
 
 

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
       user can get the cart items details ,
         manage the item quntity and delete item
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_object(self):
        item_id = self.kwargs.get('pk')
        item = get_object_or_404(CartItem, cart_item_id=item_id)
 
        if self.request.user == item.cart.user:
            return item
        else:
            raise PermissionDenied("You do not have permission to access this item's details.")
 
    def get(self, request, pk, format=None):
        try:
            instance = self.get_object()
            serializer = CartItemSerializer(instance)
            return Response({
                "status": "success",
                "message": "Item details retrieved successfully",
                "body": serializer.data,
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                "status": "not found",
                "message": "Item does not exist",
            }, status=status.HTTP_404_NOT_FOUND)
 
    def put(self, request, pk, format=None):
        instance = self.get_object()
        serializer = CartItemSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Successfully Updated!",
                "body": serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Validation error",
                "body": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
 
    def patch(self, request, pk, format=None):
        instance = self.get_object()
        serializer = CartItemSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Successfully patched!",
                "body": serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Validation error",
                "body": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk, format=None):
        item = self.get_object()
        try:
            item.delete()
            return Response({
                "status": "success",
                "message": "Item deleted"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Item Deletion Failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AddressCreateView(generics.CreateAPIView):
    """
       user can create an address for shipping an order
    
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        # Check if the user already has an address
        existing_address = Address.objects.filter(user=request.user).first()

        if existing_address:
            return Response({"message": "You have already created an address",
                  "data": AddressSerializer(existing_address).data}, 
                  status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Ensure that the address is associated with the current user
            serializer.save(user=request.user)

            return Response({"message": "Address added successfully", "data": serializer.data}, 
                            status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"message": "Address with the same user already exists"}, 
                            status=status.HTTP_400_BAD_REQUEST)



class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
       user can manage their own address 
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            # Retrieve the address based on the provided pk
            return Address.objects.get(pk=self.kwargs['pk'], user=self.request.user)
        except Address.DoesNotExist:
            raise Http404

        
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = AddressSerializer(instance)
            return Response({
                "status": "success",
                "message": "Address details retrieved successfully",
                "body": serializer.data,
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                "status": "not found",
                "message": "Address does not exist",
            }, status=status.HTTP_404_NOT_FOUND)
 
 
 
    def put(self, request, pk, format=None):
        instance = self.get_object()
        serializer = AddressSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Address Successfully Updated!",
                "body": serializer.data,
            }, status=200)
 
 
    def patch(self, request, pk, format=None):
        instance = self.get_object()
        serializer = AddressSerializer(instance, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Address Successfully patched!",
                "body": serializer.data,
            }, status=200)
 
 
    def delete(self, request, pk, format=None):
        address = self.get_object()
        try:
            address.delete()
            return Response({
                "Status": "Success",
                "Message": " Address deleted"
            }, status=204)
        except:
            return Response({
                "Status": "Failed",
                "Message": "Address Deletion Failed"
            }, status=500)



class OrderUserReviewView(APIView):
    """
       users can review their order before order placement
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        shipping_address = Address.objects.filter(user=request.user).first()

        # Check if the cart is empty
        if not user_cart.items.exists():
            return Response({'error': 'Cannot review an order with an empty cart'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        cart_items_serializer = CartItemSerializer(user_cart.items.all(), many=True)
        shipping_address_serializer = AddressSerializer(shipping_address)
        total_price = user_cart.total_price

        # Create the order review data
        order_review_data = {
            'cart_items': cart_items_serializer.data,
            'shipping_address': shipping_address_serializer.data,
            'total_price': total_price,
           
        }

        return Response(order_review_data)




# class OrderPlaceView(generics.CreateAPIView):
#     serializer_class = OrderItemSerializer
 
#     def create(self, request, *args, **kwargs):
#         try:
#             # Retrieve or create the user's cart
#             user_cart, created = Cart.objects.get_or_create(user=request.user)
 
           
#             shipping_address = get_object_or_404(Address, user=request.user)
 
 
#             # Check if the cart is empty
#             if not user_cart.items.exists():
#                 return Response({'error': 'Cannot place an order with an empty cart'}, status=status.HTTP_400_BAD_REQUEST)
 
#             # Create an order
#             order = Order.objects.create(user=request.user, total_price=user_cart.total_price, shipping_address=shipping_address)
 
#             for cart_item in user_cart.items.all():
#                 # Create OrderItem for each CartItem
#                 order_item = OrderItem.objects.create(
#                     order=order,
#                     product=cart_item.product,
#                     user=request.user,  # Set the user field with the correct value
#                     quantity=cart_item.cart_quantity,  # Use cart quantity for order item
#                     individual_price=cart_item.individual_price,
#                     total_amount=cart_item.total_amount
#                 )
 
#                 # Link the OrderItem to the CartItem
#                 cart_item.order_item = order_item
#                 cart_item.save()
 
#             # Clear the cart after placing the order
#             user_cart.items.all().delete()
#             user_cart.total_price = 0
#             user_cart.save()
 
#             # Serialize and return order details
#             serializer = OrderItemSerializer(order.items.all(), many=True)
 
#             success_message = 'Order placed successfully!'
#             return Response({'message': success_message, 'order_details': serializer.data}, status=status.HTTP_201_CREATED)
 
       
#         except ObjectDoesNotExist:
#             return Response({'error': 'Error placing the order'}, status=status.HTTP_400_BAD_REQUEST)



class OrderPlaceView(generics.CreateAPIView):
    """
      user can place their orders
    """
    serializer_class = OrderSerializer  


    def create(self, request, *args, **kwargs):
        try:
            # Retrieve or create the user's cart
            user_cart, created = Cart.objects.get_or_create(user=request.user)

            shipping_address = get_object_or_404(Address, user=request.user)

            if not user_cart.items.exists():
                return Response({'error': 'Cannot place an order with an empty cart'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # Create an order
            order = Order.objects.create(user=request.user, total_price=user_cart.total_price, 
                                         shipping_address=shipping_address)

            for cart_item in user_cart.items.all():
                # Create OrderItem for each CartItem
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    user=request.user,
                    quantity=cart_item.cart_quantity,
                    individual_price=cart_item.individual_price,
                    total_amount=cart_item.total_amount
                )

                # Link the OrderItem to the CartItem
                cart_item.order_item = order_item
                cart_item.save()

            # Clear the cart after placing the order
            user_cart.items.all().delete()
            user_cart.total_price = 0
            user_cart.save()

    
            serializer = OrderSerializer(order)
            return Response({'message': 'Order placed successfully!', 'order_details': serializer.data},
                             status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            return Response({'error': 'Error placing the order'}, status=status.HTTP_400_BAD_REQUEST)



class OrderHistoryPagination(PageNumberPagination):
    page_size = 5
 
class OrderHistoryView(generics.ListAPIView):
    """
       users can view their previous orders in order history
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderHistoryPagination
 
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')