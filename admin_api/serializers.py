from accounts.models import *
from cart.serializers import *
from rest_framework import serializers



class ListUsersSerializer(serializers.ModelSerializer):
    """
       Admin List Users Serializer
    """
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "status",
            
        ]


class CategorySerializer(serializers.ModelSerializer):

    """
       Serializer for category
    """
    category_name =serializers.CharField(required=True, allow_null = False)
    category_images = serializers.ImageField(required=False, allow_null=True)
   
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'category_images']
 
 

        
class CreateProductSerializer(serializers.ModelSerializer):

    """
        Serializer for product
    """
    # Use CharField instead of ListField for 'categories'
    categories = serializers.CharField(write_only=True)
 
    # Use CategorySerializer for 'category_details'
    category_details = CategorySerializer(source='categories', read_only=True, many=True)
 
    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "description",
            "price",  
            "quantity",
            "product_images",
            "categories",
            "category_details",
        ]
 
    def create(self, validated_data):
        # Pop the 'categories' data from validated_data
        categories_data = validated_data.pop('categories', '')
 
        # Split the comma-separated values into a list of integers
        category_ids = [int(cat_id.strip()) for cat_id in categories_data.split(',') if cat_id.strip()]
 
        # Create the product without assigning 'categories'
        product = Product.objects.create(**validated_data)
 
        # Add categories to the created product using set()
        product.categories.set(category_ids)
 
        return product
    


class AdminReviewUserSerializer(serializers.ModelSerializer):

    """
       Admin Review User Serializer
    """
    
    class Meta:
        model = CustomUser
        fields = [
            "username",
        ]



class AdminReviewSerializer(serializers.ModelSerializer):
    """
       Admin Review Serializer
    """
    user = AdminReviewUserSerializer()
    class Meta:
        model = Review
        exclude = ['product']



class DeleteReviewSerializer(serializers.Serializer):
    """
      Delete Review Serializer
    """
    review_id = serializers.IntegerField()

 
class ProductSerializer(serializers.ModelSerializer):
    """
        Details of products
    """
    category_details = CategorySerializer(many=True, source='categories' ,read_only=True)
    categories = serializers.CharField(write_only=True)
    reviews = AdminReviewSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "description",
            "price",  
            "quantity",
            "product_images",
            "categories",
            "category_details",
            "reviews"

            
           
        ]
    


class OrderItemSerializer(serializers.ModelSerializer):

    """
       Order Item  Serializer 
    """
    product_name = serializers.CharField(source='product.product_name')
    
    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'product_name', 'quantity', 'individual_price', 'total_amount']



class OrderSerializer(serializers.ModelSerializer):
    """
       Order Serializer include items details and address
    """

    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'



class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    """
       Update Order Status Serializer
    """
    class Meta:
        model = Order
        fields = ['status']

