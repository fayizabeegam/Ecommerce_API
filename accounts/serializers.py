from .models import*
from admin_api.serializers import *
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    UserRegistrationSerializer for register a user
    
    """
    password = serializers.CharField(style={"input_type":"password"})
    first_name = serializers.CharField(required = True, allow_null = False)
    last_name = serializers.CharField(required = True, allow_null = False)
   
    class Meta:
        model = CustomUser
        fields = [
            'first_name','last_name',
            'username', 'password', 
            'email',
        ]
    
    def validate_password(self, attrs):
        password = attrs
        alphabets = digits = special = 0
        password_rule = PasswordRule.objects.filter(status=PasswordRule.ACTIVE).first()
 
        for char in password:
            if char.isalpha():
                alphabets += 1
            elif char.isdigit():
                digits += 1
            else:
                special += 1
 
        if (
            password_rule.minimum_characters > len(password)
            or password_rule.maximum_characters < len(password)
        ):
            raise serializers.ValidationError({
                'Status': '1',
                'Message': 'Password length must be between {} and {} characters.'.format(
                    password_rule.minimum_characters, password_rule.maximum_characters
                ),
            })
 
        if special < password_rule.special_characters or special == 0:
            raise serializers.ValidationError({
                'Status': '1',
                'Message': 
                'The password must contain at least one special character and at most {} special characters.'.format(
                    password_rule.special_characters
                ),
            })
 
        if digits < password_rule.uppercase:
            raise serializers.ValidationError({
                'Status': '1',
                'Message': 'The password must contain at least {} digit(s).'.format(password_rule.uppercase),
            })
 
        return attrs



    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
        )
        return user
    


class LoginSerializer(serializers.Serializer):
    """
       Login Serializer for login a registered user
    """
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(style={"input_type":"password"})



class LoginResponseSerializer(serializers.ModelSerializer):
    """
       Login Response Serializer to get the user details and tokens
    """
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()

    def get_refresh_token(self,instance):
        return str(RefreshToken.for_user(instance))
    def get_access_token(self,instance):
        return str(RefreshToken.for_user(instance).access_token)

    class Meta:
        model = CustomUser
        fields =[
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "access_token",
            "refresh_token"
        ]



class UserDetailSerializer(serializers.ModelSerializer):
    """
       User Details Serializer
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
            "status"
           
        ]



class ReviewUserSerializer(serializers.ModelSerializer):
    """
       Review User Serializer to get the reviewed username
    """
    
    class Meta:
        model = CustomUser
        fields = [
            "username",
        ]



class CreateReviewSerializer(serializers.ModelSerializer):
    """
    Create Review Serializer to create a review for a product
    """
    class Meta:
        model = Review
        fields = [ 'review_content', 'rating','review_images']



class ReviewSerializer(serializers.ModelSerializer):
    """
      Review Serializer
    """
    user = ReviewUserSerializer()
    class Meta:
        model = Review
        exclude = ['product']



class ProductDetailSerializer(serializers.ModelSerializer):
    """
      Product Details Serializer to get product details, 
      include categories, category_details and product review
    """
    category_details = CategorySerializer(many=True, source='categories' ,read_only=True)
    categories = serializers.CharField(write_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

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
            "reviews",
        ]


