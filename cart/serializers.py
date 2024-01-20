from accounts.models import *
from rest_framework import serializers



class CartProductSerializer(serializers.ModelSerializer):
    """
     Serializer for cart products 
    
    """
   
    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "description",
            "price",  
            "quantity",
            "product_images",
            
           
        ]



class CartItemSerializer(serializers.ModelSerializer):

    """
      serializer for cart items
    """
    product = CartProductSerializer(read_only=True)
 
    class Meta:
        model = CartItem
        fields = ['cart_item_id',
                  'product', 'cart_quantity', 
                  'individual_price', 'total_amount'
                ]
 


 
class CartSerializer(serializers.ModelSerializer):

    """
       Cart Serializer
    """
    items = CartItemSerializer(many=True, read_only=True)
 
    class Meta:
        model = Cart
        fields = ['cart_id','user', 
                  'created_at', 'items', 
                  'total_price'
                ]




class AddressUserSerializer(serializers.ModelSerializer):

    """
       serializer for users address create
    """
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
           
        ]



class AddressSerializer(serializers.ModelSerializer):

    """
       users address details
    
    """
    address_user = AddressUserSerializer(source='user', read_only=True)
    class Meta:
        model = Address
        fields = [
               'address_id','address_user','address_line_1',
              'address_line_2', 'phone_number', 'city', 
              'state', 'zip_code', 'country', 'type'
        ]



class OrderReviewSerializer(serializers.Serializer):
    """
       Order Review Serializer
    """

    cart_items = CartItemSerializer(many=True)
    shipping_address = AddressSerializer()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    


class OrderItemSerializer(serializers.ModelSerializer):
    """
      Orders items serializer
    
    """
    product_name = serializers.SerializerMethodField()

 
    class Meta:
        model = OrderItem
        fields = ['order_item_id','product_name', 
                  'quantity', 'individual_price', 
                  'total_amount', 'order',
                    'product', 'user'
                ]
 
    def get_product_name(self, instance):
        return instance.product.product_name if instance.product else None
 
 
class OrderSerializer(serializers.ModelSerializer):
    """
       Order Serializer 
    """
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
   
    class Meta:
        model = Order
        fields = '__all__'