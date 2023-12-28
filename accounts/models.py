from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from decimal import Decimal
# Create your models here.

"""
   user model

"""
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    
    ACTIVE = 0
    INACTIVE = 1
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    )
 

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_joined = models.DateTimeField(default=timezone.now)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def has_perm(self, perm, obj=None):
        # Handle global permissions here
        return self.is_staff

    def has_module_perms(self, app_label):
        # Handle app-specific permissions here
        return self.is_staff

    def __str__(self):
        return self.email



class PasswordRule(models.Model):
    ACTIVE = 0
    INACTIVE = 1
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    )
    minimum_characters = models.PositiveSmallIntegerField(null=True, blank=True)
    maximum_characters = models.PositiveSmallIntegerField(null=True, blank=True)
    special_characters = models.PositiveSmallIntegerField(null=True, blank=True)
    uppercase = models.PositiveSmallIntegerField(null=True, blank=True)
    lowercase = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
  


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    category_images = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.category_name
 
 

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category)
    quantity = models.PositiveIntegerField()
    product_images = models.ImageField(upload_to='product_images/', null=True, blank=True)
 
    def __str__(self):
        return self.product_name



class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    review_content = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review_images = models.ImageField(upload_to='review_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.user.username} - {self.product.product_name} - {self.rating} stars"




class Address(models.Model):
    TYPE_CHOICES = (
        ('Home' ,'Home' ),
        ('Office', 'Office'),
    )
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Home')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}- {self.city}, {self.state} - {self.type} Address"




class Order(models.Model):
 
    STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Dispatched','Dispatched'),
        ('Delivered', 'Delivered'),
    )
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')    
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"
   
 
 
class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    individual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
 
    def __str__(self):
        return f"orderitem #{self.product.product_name}by{self.user.username}"
 

 
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
   
    def __str__(self):
        return f"cart  #{self.cart_id}for {self.user.username}"
 
 
 
class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)  
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_quantity = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    individual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_item = models.OneToOneField(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
 
    def __str__(self):
        return f"CartItem #{self.cart_item_id} for {self.product.product_name}by{self.cart.user.username}"
    
    def save(self, *args, ** kwargs):
        self.individual_price = self.product.price
        self.total_amount = self.individual_price * self.cart_quantity
        super().save(*args, ** kwargs)
        cart_items = self.cart.items.all()
        self.cart.total_price = sum(item.total_amount for item in cart_items)
        self.cart.save()